"""Vulture whitelist — false positives for dead code analysis.

These symbols are used at runtime by frameworks (FastAPI, Pydantic, etc.)
but appear unreferenced in static analysis.
"""

# FastAPI route handlers (registered via decorators / include_router)
health_check  # noqa: F821
list_sessions  # noqa: F821
create_session  # noqa: F821
get_session  # noqa: F821
delete_session  # noqa: F821
get_recordings  # noqa: F821
get_band_definitions  # noqa: F821
list_protocols  # noqa: F821
get_protocol  # noqa: F821
lsl_available  # noqa: F821
list_streams  # noqa: F821
lsl_status  # noqa: F821

# WebSocket endpoints (registered via @app.websocket decorator)
viewer_websocket  # noqa: F821
eeg_websocket  # noqa: F821
neurofeedback_websocket  # noqa: F821

# FastAPI app + factory + settings accessor
app  # noqa: F821
create_app  # noqa: F821
get_settings  # noqa: F821

# Pydantic model fields (accessed by framework serialization)
SessionCreate.name  # noqa: F821
SessionCreate.protocol  # noqa: F821
SessionResponse.id  # noqa: F821
SessionResponse.name  # noqa: F821
SessionResponse.protocol  # noqa: F821
SessionResponse.created_at  # noqa: F821
SessionResponse.status  # noqa: F821

# Pydantic Settings fields (populated from environment variables)
Settings.host  # noqa: F821
Settings.port  # noqa: F821
Settings.cors_origins  # noqa: F821
Settings.sample_rate  # noqa: F821
Settings.n_channels  # noqa: F821
Settings.notch_freq  # noqa: F821
Settings.bandpass_low  # noqa: F821
Settings.bandpass_high  # noqa: F821
Settings.earthsync_url  # noqa: F821
Settings.earthsync_station_id  # noqa: F821
Settings.brainflow_board_id  # noqa: F821
Settings.brainflow_serial_port  # noqa: F821
Settings.lsl_stream_type  # noqa: F821
Settings.lsl_buffer_seconds  # noqa: F821
Settings.model_config  # noqa: F821

# Dataclass fields (neurofeedback)
BandTarget.name  # noqa: F821
BandTarget.low_hz  # noqa: F821
BandTarget.high_hz  # noqa: F821
BandTarget.target  # noqa: F821
BandTarget.threshold_percentile  # noqa: F821
NFProtocol.name  # noqa: F821
NFProtocol.description  # noqa: F821
NFProtocol.evidence_level  # noqa: F821
NFProtocol.electrode  # noqa: F821
NFProtocol.reference  # noqa: F821
NFProtocol.bands  # noqa: F821
NFProtocol.session_duration_s  # noqa: F821
NFProtocol.baseline_duration_s  # noqa: F821
FeedbackState.reward  # noqa: F821
FeedbackState.inhibit  # noqa: F821
FeedbackState.reward_value  # noqa: F821
FeedbackState.inhibit_value  # noqa: F821

# Service public API (used via instances, not always directly referenced)
EEGClassifier.load  # noqa: F821
EEGClassifier.predict  # noqa: F821
EEGClassifier.classes  # noqa: F821
ArtifactRejector.calibrate  # noqa: F821
ArtifactRejector.process  # noqa: F821
EEGProcessor.reject_artifacts  # noqa: F821
EEGProcessor.compute_psd  # noqa: F821
EEGProcessor.compute_band_powers  # noqa: F821
NeurofeedbackEngine.add_baseline_sample  # noqa: F821
NeurofeedbackEngine.calibrate  # noqa: F821
NeurofeedbackEngine.evaluate  # noqa: F821
LSLInlet.is_available  # noqa: F821
LSLInlet.resolve_streams  # noqa: F821
LSLInlet.connect  # noqa: F821
LSLInlet.disconnect  # noqa: F821
LSLInlet.pull_chunk  # noqa: F821
LSLInlet.get_channel_count  # noqa: F821
LSLInlet.get_sample_rate  # noqa: F821

# broadcast helper (called from ws handler)
broadcast_to_viewers  # noqa: F821
