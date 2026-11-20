# Architecture Views Template (C4)

**Authors:** Haresh V. Parekh

---

Copy the blocks below into `docs/architecture/` in the project. The views are living documents: they
describe the system as it is now, and they change in the same PR as the code they describe. A
decision about why the system looks this way goes in an ADR (`adr-template.md`), which links to the
view; the view never carries the decision's reasoning.

Diagrams are written as Mermaid C4 blocks so they render in the repository host and diff in review.
A project that already standardizes on another text format (PlantUML, Structurizr DSL) may keep it,
declared in CLAUDE.md. A diagram that exists only as an exported image is not acceptable: nobody can
review a change to it.

## Folder

```
docs/architecture/
  context.md                 C4 Level 1: the system, its actors, adjacent systems
  containers.md              C4 Level 2: services, data stores, queues, execution environments
  components-<container>.md  C4 Level 3: one file per container whose internals need it
```

Level 4 (code) is not drawn. The source tree, laid out per `micro/project-structure.md`, is that level.

## Header for every file

````markdown
Status: Current
Last Reviewed: YYYY-MM-DD
Owner: [team or individual]
Decisions: ADR-NNN, ADR-NNN
Specs: .specs/<feature-slug> (features that changed this view)
````

`Decisions` lists the ADRs that shaped what is drawn. `Specs` lists the features whose `design.md`
added or changed an element. Both let a reader find the reasoning without it living in the diagram.

## context.md

````markdown
# System Context: [System name, in Terminology Lock terms]

[Two sentences: what the system does and for whom.]

```mermaid
C4Context
  title System Context: [System name]
  Person(user, "[Actor]", "[What they do with the system]")
  System(sys, "[System name]", "[One-line responsibility]")
  System_Ext(ext, "[Adjacent system]", "[What it provides or consumes]")
  Rel(user, sys, "[Verb phrase]")
  Rel(sys, ext, "[Verb phrase]", "[protocol]")
```

## Actors and adjacent systems
| Name | Kind | Interaction | Owner |
|---|---|---|---|
| [name] | Person / External system | [what crosses the boundary] | [team or vendor] |
````

## containers.md

````markdown
# Containers: [System name]

```mermaid
C4Container
  title Containers: [System name]
  Person(user, "[Actor]")
  System_Boundary(sys, "[System name]") {
    Container(api, "[Service]", "[Runtime]", "[One responsibility]")
    ContainerDb(db, "[Store]", "[Engine]", "[What it holds]")
    ContainerQueue(q, "[Queue]", "[Broker]", "[What flows through it]")
  }
  System_Ext(ext, "[Adjacent system]")
  Rel(user, api, "[Verb phrase]", "HTTPS")
  Rel(api, db, "Reads and writes", "SQL")
  Rel(api, ext, "[Verb phrase]", "HTTPS")
```

## Container inventory
| Container | Responsibility | Owns data | Contract | Trust boundary |
|---|---|---|---|---|
| [name] | [one responsibility] | [yes / no, which] | [link to API or event contract] | [inside / edge / external] |
````

The trust-boundary column is what `eng-os-security-practices` reads when it draws a threat model.
The contract column links to `docs/contracts/` or the OpenAPI file rather than restating it.

## components-[container].md

Add this file only when the container's internals materially affect correctness, scale, or
reviewability (the rule in `meso/system-design.md`).

````markdown
# Components: [Container name]

```mermaid
C4Component
  title Components: [Container name]
  Container_Boundary(c, "[Container name]") {
    Component(ctl, "[Capability] controller", "[Framework]", "[Responsibility]")
    Component(svc, "[Capability] service", "[Language]", "[Responsibility]")
    Component(repo, "[Capability] repository", "[Library]", "[Responsibility]")
  }
  Rel(ctl, svc, "Calls")
  Rel(svc, repo, "Calls")
```
````

## When a view must change

A PR that does any of the following updates the matching view in the same PR:

| Change | View |
|---|---|
| New or removed external actor or adjacent system | `context.md` |
| New, removed, split, or merged service, data store, queue, or scheduled job | `containers.md` |
| New or changed trust boundary, or a new owner for a container | `containers.md` |
| A container's internal responsibilities reorganized | `components-<container>.md` |

A change to code inside an existing component, with no new boundary or dependency, does not touch the views.
