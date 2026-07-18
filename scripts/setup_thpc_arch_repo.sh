#!/usr/bin/env bash
set -e

BASE="$HOME/dev/The_Talking_Heads/thpc-v2-architecture"

echo "Creating THPC v2 architecture repo at: $BASE"

# Root and README
mkdir -p "$BASE"
touch "$BASE/00-README.md"

# 01 - Architecture Vision
mkdir -p "$BASE/01-Architecture-Vision"
touch "$BASE/01-Architecture-Vision/AV-01-Executive-Summary.md"
touch "$BASE/01-Architecture-Vision/AV-02-Scope-and-Principles.md"
touch "$BASE/01-Architecture-Vision/AV-03-Stakeholders-and-Concerns.md"
touch "$BASE/01-Architecture-Vision/AV-04-High-Level-Value-Proposition.md"

# 02 - Business Architecture
mkdir -p "$BASE/02-Business-Architecture"
touch "$BASE/02-Business-Architecture/BA-01-Value-Streams.md"
touch "$BASE/02-Business-Architecture/BA-02-Business-Capabilities.md"
touch "$BASE/02-Business-Architecture/BA-03-Business-Processes.md"
touch "$BASE/02-Business-Architecture/BA-04-Persona-Definitions.md"
touch "$BASE/02-Business-Architecture/BA-05-Business-Service-Model.md"

# 03 - Application Architecture
mkdir -p "$BASE/03-Application-Architecture"
touch "$BASE/03-Application-Architecture/AA-01-Application-Services.md"
touch "$BASE/03-Application-Architecture/AA-02-Information-Flow.md"
touch "$BASE/03-Application-Architecture/AA-03-Provider-Model.md"
touch "$BASE/03-Application-Architecture/AA-04-Application-Interactions.md"

# 04 - Technology Architecture
mkdir -p "$BASE/04-Technology-Architecture"
touch "$BASE/04-Technology-Architecture/TA-01-Execution-Context.md"
touch "$BASE/04-Technology-Architecture/TA-02-Provider-Wrapper-Contracts.md"
touch "$BASE/04-Technology-Architecture/TA-03-Tech-Stack.md"
touch "$BASE/04-Technology-Architecture/TA-04-GPU-Scheduling.md"
touch "$BASE/04-Technology-Architecture/TA-05-CLI-and-Config-Architecture.md"
touch "$BASE/04-Technology-Architecture/TA-06-Microtools.md"

# 05 - Roadmap and Migration
mkdir -p "$BASE/05-Roadmap-and-Migration"
touch "$BASE/05-Roadmap-and-Migration/RM-01-MVP-Scope.md"
touch "$BASE/05-Roadmap-and-Migration/RM-02-Roadmap.md"
touch "$BASE/05-Roadmap-and-Migration/RM-03-Migration-Plan.md"

# 06 - Management (governance, traceability, ADRs)
mkdir -p "$BASE/06-Management"
touch "$BASE/06-Management/MG-01-Architecture-Principles.md"
touch "$BASE/06-Management/MG-02-Requirements-Traceability.md"
touch "$BASE/06-Management/MG-03-ADRs.md"

echo "Done. Structure created."

