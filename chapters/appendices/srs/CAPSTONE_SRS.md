**Software Requirements**  
**Specification**

IEEE 830 / ISO·IEC·IEEE 29148 Format

**\[Capstone Tile\]**  
Version x.x

\[Date\]

By

\[Member 1\]

\[Member 2\]

…

\[name\]

Faculty Adviser

# **Revision History** {#revision-history}

| Date | Version | Description | Author |
| :---- | :---- | :---- | :---- |
| \[Date\] | 0.1 | Initial draft | \[Name\] |
| \[Date\] | 1.0 | Baseline release | \[Name\] |

[Revision History	2](#revision-history)

[Table of Contents	4](#table-of-contents)

[1\. Introduction	5](#1.-introduction)

[1.1 Purpose	5](#1.1-purpose)

[1.2 Document Conventions	5](#1.2-document-conventions)

[1.3 Intended Audience and Reading Suggestions	5](#1.3-intended-audience-and-reading-suggestions)

[1.4 Product Scope	6](#1.4-product-scope)

[1.5 References	6](#1.5-references)

[2\. Overall Description	7](#2.-overall-description)

[2.1 Product Perspective	7](#2.1-product-perspective)

[2.2 Product Functions	7](#2.2-product-functions)

[2.3 User Classes and Characteristics	7](#2.3-user-classes-and-characteristics)

[2.4 Operating Environment	8](#2.4-operating-environment)

[2.5 Design and Implementation Constraints	8](#2.5-design-and-implementation-constraints)

[2.6 Assumptions and Dependencies	8](#2.6-assumptions-and-dependencies)

[3\. External Interface Requirements	10](#3.-external-interface-requirements)

[3.1 User Interfaces	10](#3.1-user-interfaces)

[3.2 Hardware Interfaces	10](#3.2-hardware-interfaces)

[3.3 Software Interfaces	10](#3.3-software-interfaces)

[3.4 Communications Interfaces	10](#3.4-communications-interfaces)

[4\. System Features	11](#4.-system-features)

[4.1 \[Feature Name 1\]	11](#4.1-[feature-name-1])

[4.1.1 Description and Priority	11](#4.1.1-description-and-priority)

[4.1.2 Stimulus/Response Sequences	11](#4.1.2-stimulus/response-sequences)

[4.1.3 Functional Requirements	11](#4.1.3-functional-requirements)

[4.2 \[Feature Name 2\]	11](#4.2-[feature-name-2])

[5\. Other Nonfunctional Requirements	12](#5.-other-nonfunctional-requirements)

[5.1 Performance Requirements	12](#5.1-performance-requirements)

[5.2 Safety Requirements	12](#5.2-safety-requirements)

[5.3 Security Requirements	12](#5.3-security-requirements)

[5.4 Software Quality Attributes	12](#5.4-software-quality-attributes)

[5.5 Business Rules	13](#5.5-business-rules)

[6\. Other Requirements	14](#6.-other-requirements)

[Appendix A: Glossary	15](#appendix-a:-glossary)

[Appendix B: Analysis Models	15](#appendix-b:-analysis-models)

# **Table of Contents** {#table-of-contents}

# **1\. Introduction** {#1.-introduction}

## **1.1 Purpose** {#1.1-purpose}

*\[Describe the purpose of this SRS and its intended audience. Identify the product whose software requirements are specified, including its revision or release number. State what the software will and will not do, if not covered in the product scope.\]*

| Examples 1\.  This SRS defines the functional and non-functional requirements for TaskFlow v1.0, a web-based task management application for small teams. 2\.  This SRS describes requirements for a hospital's Patient Records Portal v2.3, intended for developers, QA, and compliance auditors. |
| :---- |

\[This Software Requirements Specification (SRS) describes the functional and non-functional requirements for \[Product Name\] version \[x.x\]. This document is intended for use by the development team, project managers, quality assurance staff, and other stakeholders of \[Organization Name\].\]

## **1.2 Document Conventions** {#1.2-document-conventions}

*\[Describe any standards or typographical conventions followed, such as priority labels, fonts, or highlighting.\]*

| Examples 1\.  Each requirement is labeled REQ-\<section\>-\<number\> (e.g., REQ-4.1-3), with priority marked High, Medium, or Low. 2\.  Mandatory requirements use the word "shall"; optional or desired behavior uses "should" or "may". |
| :---- |

\[Requirements are prioritized as High, Medium, or Low. Each requirement is uniquely identified using the format REQ-\<Section\>-\<Number\>.\]

## **1.3 Intended Audience and Reading Suggestions** {#1.3-intended-audience-and-reading-suggestions}

*\[Describe the different types of readers the document is intended for, such as developers, project managers, testers, and users, and how the rest of the SRS is organized.\]*

| Examples 1\.  Developers should read Sections 3–5 in full; testers should focus on Section 4 (features) and Section 5 (nonfunctional requirements) to derive test cases. 2\.  Executives and sponsors may only need Section 2 (Overall Description) for a high-level understanding of scope and benefits. |
| :---- |

\[This document is organized to first present overall product context (Section 2), followed by detailed functional (Section 3–4) and non-functional (Section 5\) requirements. Developers should focus on Sections 3–5; testers should focus on Sections 4–5; managers may focus on Sections 1–2.\]

## **1.4 Product Scope** {#1.4-product-scope}

*\[Provide a short description of the software being specified and its purpose, including relevant benefits, objectives, and goals. Relate the software to corporate goals or business strategies.\]*

| Examples 1\.  TaskFlow lets small teams create, assign, and track tasks across projects, replacing the team's current spreadsheet-based tracking. 2\.  The Patient Records Portal digitizes paper-based patient charts, reducing chart retrieval time from hours to seconds. |
| :---- |

\[Provide a brief description of the product's scope, key objectives, and expected business or organizational benefits.\]

## **1.5 References** {#1.5-references}

*\[List any documents or other resources referenced in this document, including title, author, version, date, and source/location.\]*

| Examples 1\.  \[1\] Acme UI Style Guide v2, June 2026, internal wiki. 2\.  \[2\] Philippine Data Privacy Act of 2012 (RA 10173), official gazette. |
| :---- |

| Ref\# | Document Title | Version/Date | Source |
| :---- | :---- | :---- | :---- |
| \[1\] | \[Document Name\] | \[Version, Date\] | \[Location/URL\] |

# **2\. Overall Description** {#2.-overall-description}

## **2.1 Product Perspective** {#2.1-product-perspective}

*\[Describe the context and origin of the product. State whether it is a new, independent product, a replacement for an existing system, or a component of a larger system, and describe its relationship to other systems.\]*

| Examples 1\.  TaskFlow is a new standalone product that will integrate with the company's existing Slack workspace for notifications. 2\.  The Patient Records Portal replaces the hospital's legacy paper filing system and will interface with the existing Billing System. |
| :---- |

\[Describe how the product fits into a larger ecosystem or replaces/interfaces with existing systems.\]

## **2.2 Product Functions** {#2.2-product-functions}

*\[Summarize the major functions the product will perform, at a high level, without going into detail. A diagram grouping related functions may be helpful.\]*

| Examples 1\.  TaskFlow: create/assign tasks, set due dates and priorities, comment on tasks, generate weekly progress reports. 2\.  Patient Records Portal: register patients, record visit notes, schedule follow-ups, generate billing summaries. |
| :---- |

* \[Major function 1\]

* \[Major function 2\]

* \[Major function 3\]

## **2.3 User Classes and Characteristics** {#2.3-user-classes-and-characteristics}

*\[Identify the different user classes anticipated to use the product, along with important characteristics that influence requirements (e.g., technical expertise, security clearance, frequency of use).\]*

| User Class | Characteristics | Privileges/Access |
| :---- | :---- | :---- |
| \[Administrator\] | \[Technical, manages configuration\] | \[Full access\] |
| \[End User\] | \[Non-technical, daily use\] | \[Standard access\] |

## **2.4 Operating Environment** {#2.4-operating-environment}

*\[Describe the environment in which the software will operate, including hardware platform, operating system(s) and versions, and any other software components or applications it must co-exist with.\]*

| Examples 1\.  TaskFlow runs in Chrome, Firefox, and Edge (latest two versions); backend on Ubuntu 24.04. 2\.  The Patient Records Portal runs on hospital-issued Windows 11 workstations and iPads used for bedside data entry. |
| :---- |

\[Describe hardware platform, OS/browser versions, and companion software.\]

## **2.5 Design and Implementation Constraints** {#2.5-design-and-implementation-constraints}

*\[Describe any items or issues that will limit the options available to developers, such as required programming languages, tools, database integrity policies, resource limits, or regulatory requirements.\]*

| Examples 1\.  TaskFlow must use the company's existing PostgreSQL instance and must comply with the Data Privacy Act of 2012\. 2\.  The Patient Records Portal must be built using the hospital's approved HL7 FHIR standard for interoperability with lab systems. |
| :---- |

* \[Constraint 1, e.g., must comply with the Data Privacy Act\]

* \[Constraint 2, e.g., must integrate with legacy database\]

## **2.6 Assumptions and Dependencies** {#2.6-assumptions-and-dependencies}

*\[List any assumed factors (as opposed to known facts) that could affect the requirements, as well as dependencies on external factors such as third-party components.\]*

| Examples 1\.  TaskFlow assumes users have a stable internet connection and depends on the Slack API remaining backward-compatible. 2\.  The Patient Records Portal assumes hospital network uptime of 99.9% and depends on the Billing System's API for invoice generation. |
| :---- |

* \[Assumption or dependency 1\]

* \[Assumption or dependency 2\]

# **3\. External Interface Requirements** {#3.-external-interface-requirements}

## **3.1 User Interfaces** {#3.1-user-interfaces}

*\[Describe the logical characteristics of each interface between the software and its users, including screen layout or wireframes, accessibility requirements, and standard buttons/functions on every screen.\]*

## **3.2 Hardware Interfaces** {#3.2-hardware-interfaces}

*\[Describe the characteristics of each interface between the software and hardware components, including supported device types and data/control interactions.* Describe hardware interfaces, if applicable, e.g., barcode scanners, sensors, printers.\]

| Interface | Purpose | Model |
| :---- | :---- | :---- |
| barcode scanners | \[Purpose of integration\] | B11 ver 2.0 |

## **3.3 Software Interfaces** {#3.3-software-interfaces}

*\[Describe connections between this product and other software components, including databases, operating systems, tools, and libraries, including version numbers and APIs.\]*

| Interface | Purpose | Data Exchanged |
| :---- | :---- | :---- |
| \[External System/API Name\] | \[Purpose of integration\] | \[Data format/protocol\] |

## **3.4 Communications Interfaces** {#3.4-communications-interfaces}

*\[Describe requirements for communication functions, such as email, web protocols, network server communication protocols, and security or encryption standards.\]*

| Examples 1\.  All TaskFlow client-server communication occurs over HTTPS/TLS 1.2 or higher. 2\.  The Patient Records Portal sends email notifications via SMTP over TLS and transmits HL7 messages over a secure VPN tunnel. |
| :---- |

\[Describe communication protocols, e.g., HTTPS/REST, email notifications, message queues.\]

# **4\. System Features** {#4.-system-features}

*\[This section describes the major features of the product. Repeat the structure below for each feature. Each feature should be organized by relative importance or in a logical sequence.\]*

| Examples 1\.  TaskFlow — Feature: Task Creation. Description: allows a user to create a task with a title, due date, and assignee (Priority: High). Requirement: "The system shall require a title, max 100 characters, before allowing task creation." 2\.  Patient Records Portal — Feature: Patient Registration. Description: allows front-desk staff to register a new patient with name, DOB, and contact details (Priority: High). Requirement: "The system shall generate a unique patient ID upon successful registration." |
| :---- |

## **4.1 \[Feature Name 1\]** {#4.1-[feature-name-1]}

### ***4.1.1 Description and Priority*** {#4.1.1-description-and-priority}

\[Provide a short description of the feature and indicate its relative priority: High, Medium, or Low.\]

### ***4.1.2 Stimulus/Response Sequences*** {#4.1.2-stimulus/response-sequences}

\[List the sequences of user actions (stimuli) and system responses that define the behavior for this feature.\]

### ***4.1.3 Functional Requirements*** {#4.1.3-functional-requirements}

| ID | Requirement Description | Priority |
| :---- | :---- | :---- |
| REQ-4.1-1 | \[The system shall ...\] | High |
| REQ-4.1-2 | \[The system shall ...\] | Medium |

## **4.2 \[Feature Name 2\]** {#4.2-[feature-name-2]}

*\[Repeat the 4.1.1–4.1.3 structure above for each additional feature (4.2, 4.3, ...).\]*

| Examples 1\.  TaskFlow — Feature: Task Assignment. Stimulus/Response: manager selects an assignee from a dropdown → system updates the task owner → assignee receives a notification. Requirement: "The system shall allow only Project Managers to reassign tasks." (High) 2\.  TaskFlow — Feature: Task Assignment (continued). Requirement: "The system shall log the previous and new assignee for audit purposes." (Medium) |
| :---- |

# **5\. Other Nonfunctional Requirements** {#5.-other-nonfunctional-requirements}

## **5.1 Performance Requirements** {#5.1-performance-requirements}

*\[Specify numerical requirements for performance, such as response times, throughput, capacity, and degradation modes under load, for both static and dynamic conditions.\]*

| Examples 1\.  The system shall support 200 concurrent users with page load times under 2 seconds at the 95th percentile. 2\.  The system shall process report generation requests within 5 seconds for datasets up to 10,000 records. |
| :---- |

* \[e.g., The system shall support up to 500 concurrent users with a response time under 2 seconds.\]

## **5.2 Safety Requirements** {#5.2-safety-requirements}

*\[Specify requirements to protect against loss, damage, or harm resulting from software faults, including safeguards or actions to prevent such losses.\]*

| Examples 1\.  The system shall perform automated daily backups retained for 30 days. 2\.  The system shall alert administrators if a scheduled backup fails. |
| :---- |

* \[e.g., Automatic data backups shall occur every 24 hours.\]

## **5.3 Security Requirements** {#5.3-security-requirements}

*\[Specify requirements regarding security or privacy, including data encryption, authentication, authorization levels, and audit logging.\]*

| Examples 1\.  All passwords shall be stored using bcrypt hashing. 2\.  Only Project Managers may delete tasks; all deletions shall be logged with a timestamp and user ID. |
| :---- |

* \[e.g., All passwords shall be stored using a salted hash. Access shall be role-based.\]

## **5.4 Software Quality Attributes** {#5.4-software-quality-attributes}

*\[Specify additional quality characteristics important to stakeholders, such as adaptability, availability, maintainability, portability, reliability, reusability, and usability, with measurable criteria where possible.\]*

| Examples 1\.  The system shall maintain 99.5% uptime measured monthly. 2\.  The system shall be maintainable such that a new feature module can be added without modifying core task logic. |
| :---- |

* \[e.g., The system shall achieve 99.5% uptime monthly.\]

## **5.5 Business Rules** {#5.5-business-rules}

*\[List operating principles about the product, such as which user classes can perform which operations under what circumstances.\]*

| Examples 1\.  A task cannot be marked "Complete" until all of its subtasks are complete. 2\.  A task's due date cannot be set earlier than its creation date. |
| :---- |

* \[e.g., Only Administrators may modify user roles.\]

# **6\. Other Requirements** {#6.-other-requirements}

*\[Define any other requirements not covered elsewhere, such as legal/regulatory requirements, internationalization needs, or reuse objectives. Add subsections as needed.\]*

| Examples 1\.  The system shall support English and Filipino language toggling. 2\.  All user data shall be retained per the Data Privacy Act's minimum retention rules. |
| :---- |

\[List any additional requirements, e.g., data retention policies, licensing, internationalization/localization.\]

# **Appendix A: Glossary** {#appendix-a:-glossary}

*\[Define terms, acronyms, and abbreviations needed to interpret the SRS correctly.\]*

| Examples 1\.  Task — a single unit of work assigned to one user. 2\.  Sprint — a fixed time period (usually two weeks) during which a set of tasks is completed. |
| :---- |

| Term | Definition |
| :---- | :---- |
| \[Term\] | \[Definition\] |

# **Appendix B: Analysis Models** {#appendix-b:-analysis-models}

*\[Optionally include diagrams (not included in the main document) such as data flow diagrams, class diagrams, entity-relationship diagrams, state-transition diagrams, or use case diagrams, with appropriate context\]*

| Examples 1\.  An ER diagram showing Users, Tasks, Projects, and Comments tables and their relationships. 2\.  A state-transition diagram showing task status flow: To Do → In Progress → Review → Done. |
| :---- |

\[Insert diagrams/models here, if applicable.\]