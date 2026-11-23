# Far atoms for software

Each line is a domain and an atom. Rewrite the atom as one self-contained sentence for the slot when you use it.

## mechanism

- **biology:** *Quorum sensing.* A component acts only once enough peers signal the same state, which avoids lone false alarms.
- **biology:** *Stigmergy.* Workers coordinate through traces left in a shared environment (like ant pheromones), not through messages to each other.
- **biology:** *Apoptosis.* A unit that detects its own corrupted state destroys itself cleanly, before it harms the whole.
- **biology:** *Affinity maturation.* Many cheap variants are tried, the ones that match best are copied with small mutations, and the cycle repeats.
- **biology:** *Homeostasis.* A setpoint plus negative feedback holds a variable steady as the load changes.
- **economics:** *Auction.* A scarce resource goes to whoever bids the most value for it, which reveals true priority.
- **economics:** *Congestion pricing.* The price of using a shared resource rises with its load, so demand spreads itself out.
- **economics:** *Double-entry bookkeeping.* Every change is recorded twice in opposite accounts, so the sum always nets to zero and errors show up.
- **economics:** *Prediction market.* Participants bet on outcomes, and the aggregated price becomes a calibrated forecast.
- **logistics:** *Kanban pull with WIP limits.* Work is pulled only when the next stage has capacity, so queues cannot grow unbounded.
- **logistics:** *Cross-docking.* Inbound items are sorted straight to outbound without being stored, which removes the holding stage.
- **manufacturing:** *Andon cord.* Anyone may stop the whole line the moment they see a defect, so problems are fixed at their source.
- **manufacturing:** *Poka-yoke.* The shape of the process makes the wrong action physically impossible.
- **games:** *Dynamic difficulty adjustment.* The challenge tunes itself to observed performance, keeping the user in flow.
- **games:** *Save points.* State is snapshotted at known-good moments, so failure costs only progress since the last checkpoint.
- **games:** *Seeded procedural generation.* A small seed deterministically expands into large content, so you store the seed, not the content.
- **games:** *Fog of war.* Each actor sees only what is near it, which keeps decisions local and cheap.
- **physics:** *Simulated annealing.* Accept worse moves with a probability that falls over time, to escape local optima.
- **physics:** *Hysteresis.* Use different thresholds for switching on and switching off, so the system does not flap at the boundary.
- **aviation:** *Triple modular redundancy.* Three independent computations vote, and the majority wins.
- **law:** *Precedent.* Past decided cases bind future similar ones, giving consistency without enumerating rules.
- **law:** *Escrow.* A neutral holder releases value only when both sides' conditions are met.
- **law:** *Statute of limitations.* Claims expire after a fixed time, which bounds how much history must be kept.
- **medicine:** *Triage.* Cases are sorted by urgency multiplied by salvageability, not by arrival order.
- **medicine:** *Differential diagnosis.* Keep a ranked list of competing explanations and pick the test that best splits them.
- **music:** *Call and response.* One part proposes and another answers, in a fixed turn structure.
- **film:** *Continuity script.* A running log of every state detail lets later shots stay consistent with earlier ones.
- **ecology:** *Carrying capacity.* A population self-limits to what its environment can sustain.

## constraint

- **space travel:** It must work with no network for days, and sync later.
- **ham radio:** Every message must fit in a tiny fixed budget, for example 1 KB.
- **accounting:** Every step must be fully reversible, with a full audit trail.
- **film:** It must replay deterministically from a seed and a log.
- **aviation:** It may need human attention at exactly one decision point.
- **embedded:** No dynamic memory and no new service.
- **library:** It must still work for a user who arrives in 10 years.
- **theatre:** It must degrade gracefully, so the show goes on with any one part missing.

## check

- **genetics:** *Mutation testing.* Plant small bugs. If the tests still pass, the tests are weak.
- **physics:** *Metamorphic testing.* Check relations between outputs (for example, double the input and the output doubles) when the exact answer is unknown.
- **medicine:** *Double-blind A/B.* Neither the system nor the judge knows which arm is which.
- **military:** *Red team.* A dedicated adversary tries to break it.
- **mining:** *Canary.* Expose a tiny slice first, and watch it.
- **aviation:** *Shadow mode.* Run the new path on real traffic, but only log its decisions.
- **chaos:** *Chaos experiment.* Inject real faults in production-like conditions.
- **photography:** *Golden master.* Snapshot the current output, and flag any diff.
- **science:** *Pre-registration.* Write down the expected result before running.
