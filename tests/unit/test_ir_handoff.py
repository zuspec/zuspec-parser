"""Phase-2: pssc.ir.to_core_context — type_map->type_m parity, node identity,
and IRSerializer round-trip."""
import zuspec.ir.core as ir

import pssc
from pssc.ir import to_core_context, dump_ir, DEFAULT_LAYER

SRC = "component pss_top { action A { rand bit[8] x; constraint x > 3; } }"


def _translate(tmp_path):
    p = tmp_path / "m.pss"
    p.write_text(SRC)
    return pssc.driver.translate(str(p))


def test_type_map_to_type_m_parity(tmp_path):
    ctx = _translate(tmp_path)
    core = to_core_context(ctx)
    assert isinstance(core, ir.Context)
    assert set(core.type_m.keys()) == set(ctx.type_map.keys())


def test_node_identity_preserved(tmp_path):
    ctx = _translate(tmp_path)
    core = to_core_context(ctx)
    assert all(core.type_m[k] is ctx.type_map[k] for k in ctx.type_map)


def test_driver_attaches_core_context(tmp_path):
    ctx = _translate(tmp_path)
    assert isinstance(ctx.ir_context, ir.Context)
    assert ctx.ir_context.type_m.keys() == ctx.type_map.keys()


def test_serializer_roundtrip(tmp_path):
    ctx = _translate(tmp_path)
    core = to_core_context(ctx)
    text = dump_ir(core)
    import yaml
    data = yaml.safe_load(text)
    assert data["_type"] == "Context"
    assert "_schema_version" in data and "_layer" in data
    # round-trips back through the deserializer to a Context
    deser = ir.IRDeserializer()
    deser.auto_register(ir)
    obj, layer = deser.deserialize(text)
    assert type(obj).__name__ == "Context"
    assert set(obj.type_m.keys()) == set(core.type_m.keys())
