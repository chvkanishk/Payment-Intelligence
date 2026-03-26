# PCI DSS v4.0 Quick Reference Guide

## What is PCI DSS?

The Payment Card Industry Data Security Standard (PCI DSS) is a global security standard created by the PCI Security Standards Council (PCI SSC). It was founded by American Express, Discover, JCB, Mastercard, and Visa to protect cardholder data and reduce payment card fraud.

PCI DSS applies to **all organizations** that store, process, or transmit cardholder data — including merchants, payment processors, banks, and service providers.

The current version is **PCI DSS v4.0**, released March 2022. v4.0 became the only active standard on **March 31, 2024**.

---

## Cardholder Data vs Sensitive Authentication Data

### Cardholder Data (CHD) — can be stored with protection
| Data Element | Storage Permitted | Protection Required |
|---|---|---|
| Primary Account Number (PAN) | Yes | Must be rendered unreadable |
| Cardholder Name | Yes | No special requirement |
| Expiration Date | Yes | No special requirement |
| Service Code | Yes | No special requirement |

### Sensitive Authentication Data (SAD) — MUST NOT be stored after authorization
| Data Element | Storage Permitted |
|---|---|
| Full magnetic stripe data | Never |
| CAV2 / CVC2 / CVV2 / CID (security codes) | Never |
| PIN / PIN Block | Never |

---

## The 12 PCI DSS Requirements

PCI DSS v4.0 is organized into 6 goals and 12 requirements:

### Goal 1: Build and Maintain a Secure Network

**Requirement 1: Install and Maintain Network Security Controls**
- Deploy firewalls between untrusted networks and the cardholder data environment (CDE)
- Deny all traffic not explicitly required
- Document all connections to cardholder data
- Review firewall rules every 6 months
- Use stateful inspection — block inbound and outbound traffic that is not necessary

**Requirement 2: Apply Secure Configurations to All System Components**
- Change all vendor-supplied default passwords before deployment
- Develop configuration standards for all system components
- Enable only necessary services, protocols, and ports
- Encrypt all non-console administrative access
- Document security configuration standards and keep them current

---

### Goal 2: Protect Account Data

**Requirement 3: Protect Stored Account Data**
- Keep cardholder data storage to the minimum necessary
- Never store sensitive authentication data after authorization
- Mask PAN when displayed — show only first 6 and last 4 digits maximum
- Render PAN unreadable using strong cryptography (AES-256, RSA-2048+)
- Protect cryptographic keys used to encrypt cardholder data
- Document and implement data retention and disposal policies
- Delete cardholder data when no longer needed

**Requirement 4: Protect Cardholder Data with Strong Cryptography During Transmission**
- Use strong cryptography (TLS 1.2 or higher) for transmitting cardholder data over open, public networks
- Never send PANs via end-user messaging (email, chat, SMS)
- Maintain an inventory of trusted keys and certificates
- Disable early SSL and early TLS (TLS 1.0, TLS 1.1 are not acceptable)

---

### Goal 3: Maintain a Vulnerability Management Program

**Requirement 5: Protect All Systems and Networks from Malicious Software**
- Deploy anti-malware on all systems commonly affected by malware
- Keep anti-malware solutions current and actively running
- Perform periodic scans for malware
- Protect against phishing attacks
- Review systems that are not commonly affected by malware periodically

**Requirement 6: Develop and Maintain Secure Systems and Software**
- Identify and address security vulnerabilities in a timely manner
- Apply critical patches within 1 month of release
- Protect web-facing applications against known attacks (OWASP Top 10)
- Use a web application firewall (WAF) for public-facing web applications
- Separate development and production environments
- Do not use live cardholder data in test or development environments
- Review custom code for vulnerabilities before release
- Train developers in secure coding practices at least annually

---

### Goal 4: Implement Strong Access Control Measures

**Requirement 7: Restrict Access to System Components and Cardholder Data by Business Need to Know**
- Limit access to system components to only those individuals whose job requires such access
- Assign least privilege — grant minimum access required
- Document access control policies
- Review user access rights at least every 6 months
- Remove access immediately upon termination

**Requirement 8: Identify Users and Authenticate Access to System Components**
- Assign unique IDs to all users — never share user accounts
- Enforce strong passwords: minimum 12 characters, upper + lower + number + special character
- Lock accounts after no more than 10 failed login attempts
- Set lockout duration to at least 30 minutes
- Require re-authentication after 15 minutes of inactivity
- Use multi-factor authentication (MFA) for all access to the CDE
- MFA is required for all remote network access
- Manage service account passwords and API keys securely
- Change passwords at least every 90 days (or use risk-based analysis)

**Requirement 9: Restrict Physical Access to Cardholder Data**
- Use physical access controls for all areas housing cardholder data
- Distinguish between onsite personnel and visitors
- Maintain a visitor log
- Secure all media containing cardholder data
- Destroy media containing cardholder data when no longer needed
- Protect point-of-interaction (POI) devices from tampering

---

### Goal 5: Regularly Monitor and Test Networks

**Requirement 10: Log and Monitor All Access to System Components and Cardholder Data**
- Implement audit logs for all access to cardholder data
- Log all invalid logical access attempts
- Log use of and changes to privileged accounts
- Log initialization, stopping, and pausing of audit logs
- Synchronize all system clocks via NTP
- Retain audit logs for at least 12 months, with 3 months immediately available
- Review logs daily for anomalies and suspicious activity
- Use a Security Information and Event Management (SIEM) system

**Requirement 11: Test Security of Systems and Networks Regularly**
- Test for presence of wireless access points every 3 months
- Run internal and external vulnerability scans quarterly
- Use an Approved Scanning Vendor (ASV) for external scans
- Perform penetration testing at least annually and after significant changes
- Use an intrusion detection / intrusion prevention system (IDS/IPS)
- Deploy change-detection mechanisms to alert on unauthorized modification of critical files
- Review critical file changes weekly

---

### Goal 6: Maintain an Information Security Policy

**Requirement 12: Support Information Security with Organizational Policies and Programs**
- Document and publish an information security policy
- Review the security policy at least annually
- Develop and implement a risk assessment process
- Perform a formal risk assessment at least annually
- Maintain an inventory of all system components in scope
- Implement a security awareness program — train all personnel annually
- Screen potential personnel before hiring
- Manage service providers who have access to cardholder data
- Maintain an incident response plan
- Test the incident response plan at least annually

---

## PCI DSS Compliance Levels

Compliance requirements depend on transaction volume:

### Merchant Levels

| Level | Criteria | Requirements |
|---|---|---|
| Level 1 | Over 6 million Visa/MC transactions/year | Annual on-site audit by Qualified Security Assessor (QSA), quarterly network scans |
| Level 2 | 1–6 million transactions/year | Annual Self-Assessment Questionnaire (SAQ), quarterly network scans |
| Level 3 | 20,000–1 million e-commerce transactions/year | Annual SAQ, quarterly network scans |
| Level 4 | Under 20,000 e-commerce or under 1 million total/year | Annual SAQ recommended, quarterly scans recommended |

### Service Provider Levels

| Level | Criteria | Requirements |
|---|---|---|
| Level 1 | Over 300,000 transactions/year | Annual on-site audit by QSA, quarterly network scans |
| Level 2 | Under 300,000 transactions/year | Annual SAQ, quarterly network scans |

---

## Self-Assessment Questionnaires (SAQ)

Different SAQ types apply to different business models:

| SAQ | Who It Applies To |
|---|---|
| SAQ A | Card-not-present merchants who outsource all cardholder data to PCI-compliant third parties |
| SAQ A-EP | E-commerce merchants who outsource payment processing but whose website could affect security |
| SAQ B | Merchants using imprint machines or standalone dial-out terminals only |
| SAQ B-IP | Merchants using standalone IP-connected payment terminals only |
| SAQ C | Merchants with payment application systems connected to the internet |
| SAQ C-VT | Merchants using web-based virtual terminals provided by a third party |
| SAQ D | All other merchants and service providers not covered by SAQ A–C |
| SAQ P2PE | Merchants using validated point-to-point encryption (P2PE) solutions |

---

## Key Security Controls Summary

### Cryptography Requirements
- Minimum RSA 2048-bit or ECC 224-bit for asymmetric encryption
- Minimum AES 128-bit (AES 256 recommended) for symmetric encryption
- TLS 1.2 minimum for data in transit (TLS 1.3 recommended)
- SHA-256 minimum for hashing
- Use PBKDF2, bcrypt, or scrypt for password hashing

### Network Segmentation
- Segment the cardholder data environment (CDE) from other networks
- Use firewalls, VLANs, or other network controls
- Reduce the scope of PCI DSS compliance by isolating CDE
- Document and maintain network diagrams showing CDE boundaries

### Tokenization
- Replace PAN with a non-sensitive token for storage and processing
- Tokens have no exploitable value outside the tokenization system
- Reduces PCI DSS scope significantly
- Tokens must map to PAN in a secure token vault

### Point-to-Point Encryption (P2PE)
- Encrypts cardholder data from point of interaction through decryption
- Validated P2PE solutions listed on PCI SSC website
- Significantly reduces PCI DSS scope for merchants

---

## Incident Response Requirements

Under PCI DSS Requirement 12.10, organizations must maintain an incident response plan that includes:

1. Roles and responsibilities for response team members
2. Communication procedures including notification of card brands and acquirers
3. Recovery and continuity procedures
4. Legal requirements for reporting compromises
5. Coverage for all critical system components
6. Response procedures for system alerts from IDS/IPS and change detection
7. Annual testing and review of the plan
8. Training for personnel with incident response responsibilities

---

## New in PCI DSS v4.0

Key changes from v3.2.1 to v4.0:

- **Customized approach** — organizations can now implement alternative controls to meet requirements, providing they document and test them rigorously
- **Multi-factor authentication** expanded — MFA now required for all access into the CDE, not just remote access
- **Password requirements updated** — minimum 12 characters (was 7)
- **E-commerce security** — new requirements to manage scripts on payment pages (Requirement 6.4.3 and 11.6.1)
- **Targeted risk analysis** — organizations can perform risk analysis to determine frequency of certain activities
- **Phishing protections** — new requirement to train personnel to detect phishing (Requirement 5.4.1)
- **Roles and responsibilities** — each requirement now explicitly requires documented roles and responsibilities

---

## Glossary

| Term | Definition |
|---|---|
| ASV | Approved Scanning Vendor — company approved by PCI SSC to perform external vulnerability scans |
| CDE | Cardholder Data Environment — systems that store, process, or transmit cardholder data |
| CHD | Cardholder Data — PAN, name, expiry, service code |
| PAN | Primary Account Number — the 16-digit card number |
| QSA | Qualified Security Assessor — company certified to perform PCI DSS audits |
| ROC | Report on Compliance — formal report produced by QSA after Level 1 audit |
| SAD | Sensitive Authentication Data — full magnetic stripe, CVV, PIN |
| SAQ | Self-Assessment Questionnaire — self-evaluation tool for lower-level merchants |
| P2PE | Point-to-Point Encryption — encrypts data from terminal to decryption point |
| ISA | Internal Security Assessor — individual certified to perform internal PCI audits |
