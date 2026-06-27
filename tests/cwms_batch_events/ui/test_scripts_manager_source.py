from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_FORM = ROOT / "ui" / "src" / "features" / "scripts-manager" / "ScriptForm.tsx"


def test_script_form_exposes_registry_runtime_schedule_and_size_controls():
    source = SCRIPT_FORM.read_text(encoding="utf-8")

    assert 'id="runtime"' in source
    assert "Python" in source
    assert "Node" in source
    assert "Java" in source
    assert "Shell" in source

    assert 'id="resourceProfile"' in source
    assert "Small - 1 vCPU / 2 GB" in source
    assert "Medium - 2 vCPU / 4 GB" in source
    assert "Large - 4 vCPU / 8 GB" in source

    assert 'id="scheduleMinute"' in source
    assert 'max={59}' in source
    assert 'min={0}' in source
    assert 'id="scheduleCron"' in source


def test_script_form_env_vars_are_row_based_and_guard_duplicates():
    source = SCRIPT_FORM.read_text(encoding="utf-8")

    assert "type EnvVarRow" in source
    assert "envVarRows.map" in source
    assert 'aria-label="Environment variable key"' in source
    assert "Add variable" in source
    assert "deleteEnvVarRow" in source
    assert "Environment variable keys cannot be blank" in source
    assert 'Environment variable key "${key}" is duplicated' in source
    assert "isAwsBatchReservedEnvName" in source
    assert "isBatchEventsReservedEnvName" in source
    assert "batchEventsReservedEnvNames" in source
    assert 'Environment variable key "${key}" cannot start with AWS_BATCH' in source
    assert (
        'Environment variable key "${key}" is reserved for Batch Events runtime'
        in source
    )
    assert (
        'Secret environment variable "${reservedSecretEnvName}" cannot start with AWS_BATCH'
        in source
    )
    assert (
        'Secret environment variable "${batchEventsReservedSecretEnvName}" is reserved for Batch Events runtime'
        in source
    )
    assert "border-red-500" in source


def test_script_form_delete_env_button_is_visible_red_and_sized_for_clicking():
    source = SCRIPT_FORM.read_text(encoding="utf-8")

    assert 'title="Delete environment variable"' in source
    assert 'backgroundColor: "#b91c1c"' in source
    assert 'height: "2.25rem"' in source
    assert 'width: "2.75rem"' in source
    assert 'fontSize: "1.25rem"' in source


def test_script_form_does_not_render_legacy_execution_type_control():
    source = SCRIPT_FORM.read_text(encoding="utf-8")

    assert "Execution Type" not in source
    assert 'id="executionType"' not in source
