from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_FORM = ROOT / "ui" / "src" / "features" / "scripts-manager" / "ScriptForm.tsx"
SCRIPTS_LIST = ROOT / "ui" / "src" / "features" / "scripts-manager" / "ScriptsList.tsx"
SCRIPTS_WORKSPACE = (
    ROOT / "ui" / "src" / "features" / "scripts-manager" / "ScriptsWorkspace.tsx"
)
SCRIPT_VIEW = ROOT / "ui" / "src" / "features" / "scripts-manager" / "ScriptView.tsx"
UTILS = ROOT / "ui" / "src" / "features" / "scripts-manager" / "utils.ts"


def test_script_form_exposes_registry_runtime_schedule_and_size_controls():
    source = SCRIPT_FORM.read_text(encoding="utf-8")

    assert 'id="runtime"' in source
    assert "Python" in source
    assert "Node" in source
    assert "Java" in source
    assert "Shell" in source

    assert 'id="resourceProfile"' in source
    assert "resourceProfileLabels.small" in source
    assert "resourceProfileLabels.medium" in source
    assert "resourceProfileLabels.large" in source

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


def test_script_form_exposes_source_type_and_cron_helper():
    source = SCRIPT_FORM.read_text(encoding="utf-8")

    assert "Execution Type" not in source
    assert 'id="executionType"' in source
    assert "GitHub File Path" in source
    assert "Command" in source
    assert "cwms-cli users user-ids | grep Test" in source
    assert "crontab.guru" in source
    assert 'target="_blank"' in source
    assert 'title="Open cron expression helper in a new tab"' in source


def test_script_form_exposes_repository_browser_for_github_paths():
    source = SCRIPT_FORM.read_text(encoding="utf-8")

    assert "runtimeScriptTypes" in source
    assert "(case-insensitive)" in source
    assert "directoryFromPath(form.repoPath)" in source
    assert "window.setTimeout" in source
    assert "/api/scripts/repository" in source
    assert "includeAll" in source
    assert "Browse repository" in source
    assert "Repository browser is not configured." in source
    assert "No matching scripts found." in source
    assert "selectRepositoryEntry" in source


def test_script_form_has_scrollable_editor_with_top_action_bar():
    source = SCRIPT_FORM.read_text(encoding="utf-8")

    assert "max-h-[65vh]" in source
    assert "overflow-y-auto" in source
    assert "sticky top-0" in source
    assert "formTitle" in source
    assert "Edit Script: ${script.name}" in source
    assert "New Script" in source
    assert "Configure runtime, source, schedule, roles, and environment." in source
    assert "Save changes" in source
    assert "Create script" in source


def test_scripts_manager_selector_is_stacked_scrollable_and_row_targetable():
    list_source = SCRIPTS_LIST.read_text(encoding="utf-8")
    workspace_source = SCRIPTS_WORKSPACE.read_text(encoding="utf-8")

    assert "max-h-[20vh]" in workspace_source
    assert "max-h-[45vh]" in workspace_source
    assert "flex w-full flex-col" in workspace_source
    assert "overflow-y-auto" in workspace_source
    assert "MdEdit" in list_source
    assert 'aria-label={`Edit ${script.name}`}' in list_source
    assert 'role="button"' in list_source
    assert "onKeyDown" in list_source
    assert "onClick={() => selectScript(script.id)}" in list_source


def test_scripts_manager_shows_resource_profile_sizes_on_all_surfaces():
    utils_source = UTILS.read_text(encoding="utf-8")
    list_source = SCRIPTS_LIST.read_text(encoding="utf-8")
    view_source = SCRIPT_VIEW.read_text(encoding="utf-8")

    assert "Small - 1 vCPU / 2 GB" in utils_source
    assert "Medium - 2 vCPU / 4 GB" in utils_source
    assert "Large - 4 vCPU / 8 GB" in utils_source
    assert 'defaultScheduleTimezone = "UTC"' in utils_source
    assert "scheduleTimezoneLabel(script.scheduleTimezone)" in list_source
    assert "scheduleTimezoneLabel(script.scheduleTimezone)" in view_source
    assert "resourceProfileLabel(script.resourceProfile)" in list_source
    assert "resourceProfileLabel(script.resourceProfile)" in view_source


def test_script_form_uses_searchable_valid_schedule_timezone():
    utils_source = UTILS.read_text(encoding="utf-8")
    source = SCRIPT_FORM.read_text(encoding="utf-8")

    assert "availableScheduleTimezones" in utils_source
    assert "Intl" in utils_source
    assert "supportedValuesOf" in utils_source
    assert "isValidScheduleTimezone" in utils_source
    assert 'id="scheduleTimezone"' in source
    assert 'list="schedule-timezone-options"' in source
    assert "<datalist" in source
    assert "availableScheduleTimezones.map" in source
    assert "isValidScheduleTimezone(normalizedScheduleTimezone)" in source
    assert 'Schedule timezone "${form.scheduleTimezone}" is not valid' in source
    assert "Schedule ({currentScheduleTimezone})" in source
    assert "Minute ({currentScheduleTimezone})" in source
    assert "Cron ({currentScheduleTimezone})" in source
