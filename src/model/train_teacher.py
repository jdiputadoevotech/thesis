"""Train the supervised teacher: DINOv2 with LoRA (r=8, alpha=16) plus a linear
font classifier, fitted to the font labels of the train split (Section 4.3.2).

The teacher exists only offline. Its sole output is the similarity structure
the student distills (cache_features.py --teacher); it is never on the
inference path, so its closed-set classifier never reaches a user's crop.
Its validation accuracy is a sanity check, not a thesis result.

Fits a 4 GB GPU: micro-batches of 16 with 4-step gradient accumulation
(equivalent to batch 64 -- CE is per-sample and the ViT uses LayerNorm, not
BatchNorm), fp16 autocast, gradient checkpointing.

    .venv/Scripts/python.exe src/model/train_teacher.py              # 10 epochs -> data/models/teacher10
    .venv/Scripts/python.exe src/model/train_teacher.py --limit 2000 --epochs 1 --out /tmp/teacher
"""

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from encoder import BACKBONES, ROOT, Crops, Preprocess, collate, load_rows

LORA = dict(r=8, lora_alpha=16, target_modules=["query", "value"], lora_dropout=0.1)


class Teacher(nn.Module):
    def __init__(self, n_classes):
        super().__init__()
        from peft import LoraConfig, get_peft_model
        from transformers import AutoModel
        vit = AutoModel.from_pretrained(BACKBONES["dinov2"][0])
        vit.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        self.vit = get_peft_model(vit, LoraConfig(**LORA))
        self.prep = Preprocess("dinov2")
        self.cls = nn.Linear(vit.config.hidden_size, n_classes)

    def embed(self, x):
        return self.vit(pixel_values=x).last_hidden_state[:, 0]

    def forward(self, imgs):
        return self.cls(self.embed(self.prep(imgs)))


def load_teacher(path):
    from peft import set_peft_model_state_dict
    ck = torch.load(Path(path) / "teacher.pt", map_location="cpu")
    t = Teacher(ck["n_classes"])
    set_peft_model_state_dict(t.vit, ck["lora"])
    t.cls.load_state_dict(ck["cls"])
    return t


def save_teacher(t, fonts, path):
    from peft import get_peft_model_state_dict
    path.mkdir(parents=True, exist_ok=True)
    torch.save({"n_classes": len(fonts), "fonts": fonts, "lora": get_peft_model_state_dict(t.vit),
                "cls": t.cls.state_dict()}, path / "teacher.pt")


@torch.no_grad()
def accuracy(t, loader, dev):
    t.eval()
    hit = n = 0
    for imgs, y in loader:
        with torch.autocast(dev, dtype=torch.float16, enabled=dev == "cuda"):
            hit += (t(imgs).argmax(1).cpu() == y).sum().item()
        n += len(y)
    return hit / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=10)  # plateaus by 8-10 (reports/incr2/teacher10.json)
    ap.add_argument("--micro", type=int, default=16)
    ap.add_argument("--accum", type=int, default=4)
    ap.add_argument("--lr", type=float, default=1e-4, help="LoRA lr; the classifier gets 10x")
    ap.add_argument("--limit", type=int, help="random N train rows (smoke runs)")
    ap.add_argument("--seed", type=int, default=2026)
    # Each worker process loads its own CUDA libraries; too many at once exhausts
    # the Windows pagefile (WinError 1455) long before they exhaust the GPU.
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", type=Path, default=ROOT / "data/models/teacher10")
    args = ap.parse_args()

    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    rows = load_rows()
    fonts = sorted({r["font_id"] for r in rows})
    idx = {f: i for i, f in enumerate(fonts)}
    train = [r for r in rows if r["split"] == "train"]
    val = [r for r in rows if r["split"] == "validation"]
    if args.limit:
        train = random.Random(args.seed).sample(train, args.limit)
        val = random.Random(args.seed).sample(val, args.limit // 4)
    mk = lambda rs, shuffle: torch.utils.data.DataLoader(
        Crops(rs, [idx[r["font_id"]] for r in rs]), batch_size=args.micro, shuffle=shuffle,
        num_workers=args.workers, collate_fn=collate,
        generator=torch.Generator().manual_seed(args.seed))
    train_dl, val_dl = mk(train, True), mk(val, False)

    t = Teacher(len(fonts)).to(dev)
    lora = [p for p in t.vit.parameters() if p.requires_grad]
    opt = torch.optim.AdamW([{"params": lora, "lr": args.lr},
                             {"params": t.cls.parameters(), "lr": args.lr * 10}], weight_decay=0.01)
    steps = args.epochs * len(train_dl) // args.accum
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=[args.lr, args.lr * 10], total_steps=steps + 1,
                                                pct_start=0.1)
    scaler = torch.amp.GradScaler(enabled=dev == "cuda")
    print(f"trainable {sum(p.numel() for p in lora):,} LoRA params; {len(train)} train / {len(val)} val",
          file=sys.stderr)

    best, log = -1.0, []
    for ep in range(args.epochs):
        t.train()
        for i, (imgs, y) in enumerate(train_dl):
            with torch.autocast(dev, dtype=torch.float16, enabled=dev == "cuda"):
                loss = F.cross_entropy(t(imgs), y.to(dev)) / args.accum
            scaler.scale(loss).backward()
            if (i + 1) % args.accum == 0:
                scaler.step(opt); scaler.update(); opt.zero_grad(set_to_none=True); sched.step()
            if i % 200 == 0:
                print(f"ep {ep} step {i}/{len(train_dl)} loss {loss.item() * args.accum:.3f}", file=sys.stderr)
        acc = accuracy(t, val_dl, dev)
        log.append({"epoch": ep, "val_top1": acc})
        print(f"ep {ep} val top1 {acc:.4f}", file=sys.stderr)
        if acc > best:
            best = acc
            save_teacher(t, fonts, args.out)

    # Real runs (under data/models/) report beside the other Increment 2 evidence;
    # smoke runs elsewhere keep their report next to their checkpoint.
    real = args.out.resolve().is_relative_to((ROOT / "data/models").resolve())
    report = ROOT / f"reports/incr2/{args.out.name}.json" if real else args.out / "teacher.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({"best_val_top1": best, "epochs": log, "lora": LORA,
                                  "args": {k: str(v) for k, v in vars(args).items()}}, indent=2))
    print(f"best val top1 {best:.4f} -> {args.out}")


if __name__ == "__main__":
    main()
