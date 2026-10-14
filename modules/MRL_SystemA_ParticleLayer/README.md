# MRL_SystemA_ParticleLayer v0.1

`origin_signature: MrLiouWord`

## Status

`0.1.0-draft / schema-pending`

This module expresses the three canonical System A tables as `UnifiedParticle` without changing their PostgreSQL schema:

- `mrl_persona`
- `mrl_memory`
- `mrl_file_index`

It implements the source laws from the specification:

- **LAW-0** — `origin_signature` is immutable and must be `MrLiouWord`.
- **LAW-1** — PostgreSQL on DL580 remains canonical persistence.
- **LAW-2** — conversion is additive, non-destructive, and reversible.

## Files

- `unified_particle.py` — canonical transport model.
- `MRL_SystemA_ParticleLayer.py` — adapters and LAW-2 verification.
- `tests/test_particle_layer.py` — unit tests.

## Local verification

```bash
cd modules/MRL_SystemA_ParticleLayer
python -m pip install pytest
pytest -q
```

## Integration

```python
from MRL_SystemA_ParticleLayer import MemoryAdapter

row = pg.fetchone("SELECT * FROM mrl_memory WHERE id = %s", (mid,))
adapter = MemoryAdapter()
particle = adapter.to_unified(row)

# Existing bridges may consume the canonical mapping.
mrl_payload = particle.to_mrl()

# Reversible return to the original row shape.
row_back = adapter.from_unified(particle)
assert row_back == row
```

## Deployment boundary

This package is a pure Python library. It does not open a port and does not create or alter database tables. Deploy it by copying the directory into the Python import path of `MRL_Operations_API`, `MRL_AI_OS`, or `fluin_bridge`.

Suggested Windows Server destination:

```text
D:\mrl\workspace\MRL_SystemA_ParticleLayer\
```

## Pending schema decisions

Before v0.2, confirm:

1. Whether all three tables already contain `origin_signature`.
2. Whether state-bearing fields are `JSONB` or `TEXT`.
3. Whether the tables share a foreign key or canonical `persona_id`.
4. Whether `mrl_particle` must become a fourth adapter.

Until those are confirmed, the adapter preserves the complete source row in `UnifiedParticle.state`, which provides a safe reversible baseline without inventing field mappings.

# PR #18 authority and sampling contract

`origin` and `origin_signature` are both inspected. Any populated foreign
signature makes the source `foreign_marked`, including a conflict with
`MrLiouWord` in the other field. Sources without signatures remain
`unsigned_pending`; conversion preserves their original row and provenance.

`verify_law2()` propagates the original conversion exception, including
`ParticleLayerError` for a missing identifier. A false round-trip comparison
still raises `RoundtripViolation`.

`Mrliou_MRL_build_law2_report(..., sample_n=100)` now reads at most 100 rows,
including for database cursors and infinite generators. At the limit it reports
`total_rows=None`, `total_rows_known=False`, `coverage=None`, and
`global_claim=False`. It does not fetch a 101st row to guess whether the input
ended. A shorter exhausted source has a known total. Full verification with
`sample_n=None` still consumes all rows. Explicit `count_total=True` opts into
scanning the remaining input to calculate exact totals and coverage.

Regression checks (also collected by the existing ParticleLayer pytest CI):

```bash
python -m unittest discover -s modules/MRL_SystemA_ParticleLayer/tests -p test_law_contract_regressions.py -v
```

These checks use repository data and do not establish DL580 deployment status.

