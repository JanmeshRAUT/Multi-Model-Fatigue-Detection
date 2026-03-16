import React, { useEffect, useMemo, useState } from 'react';
import { useVehicleContext } from '../context/VehicleContext';
import './Css/VehicleDashboard.css';
import './Css/VehicleShared.css';
import { Eye, Radio, AlertCircle, Loader, Gauge, Radar, Camera, Waves, Clock3 } from 'lucide-react';
import HeadPositionChart from './HeadPositionChart';
import VehicleStatus from './VehicleStatus';
import CameraModule from './CameraModule';
import EyeModel3D from './EyeModel3D';
import { getConnectionMeta } from '../utils/vehicleStatus';
import { getPerclosRiskBand } from '../utils/vehicleStatus';

const EmptyState = ({ message, loading = false }) => (
    <div className="vehicle-empty">
        <div>
            {loading ? <Loader size={24} className="spinner" /> : <AlertCircle size={24} />}
            <div>{message}</div>
        </div>
    </div>
);

const getStatusTone = (status) => {
    if (status === 'Fatigued') return 'danger';
    if (status === 'Drowsy') return 'warning';
    return 'safe';
};

const VehicleDashboard = () => {
    const { vehicleData, headPositionHistory, predictionHistory, connectionStatus } = useVehicleContext();
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (vehicleData) {
            setIsLoading(false);
        }
    }, [vehicleData]);

    const perclos = vehicleData?.perclos || {};
    const head = vehicleData?.head_position || {};

    const perclosPct = Number((perclos.perclos || 0).toFixed(1));
    const confidencePct = Math.round(((vehicleData?.prediction?.confidence || 0) * 100));
    const connectionMeta = useMemo(() => getConnectionMeta(connectionStatus), [connectionStatus]);
    const recentPredictions = useMemo(() => (predictionHistory || []).slice(-10).reverse(), [predictionHistory]);
    const trendPredictions = useMemo(() => (predictionHistory || []).slice(-24), [predictionHistory]);

    const riskBand = useMemo(() => getPerclosRiskBand(perclosPct), [perclosPct]);
    const perclosTone = perclosPct >= 45 ? 'danger' : perclosPct >= 25 ? 'warning' : 'safe';
    const hasPerclosData = Boolean(vehicleData?.perclos);
    const hasHeadData = headPositionHistory.length > 0;
    const headPosition = head.position || 'Unknown';

    const cameraOverlayMode = useMemo(() => {
        const pos = String(head.position || '').toLowerCase();
        const source = String(head.source || '').toLowerCase();
        const x = Number(head.angle_x || 0);
        const y = Number(head.angle_y || 0);
        const z = Number(head.angle_z || 0);

        const noSubject = pos === 'unknown' || source === 'none';
        if (noSubject) return 'no-subject';

        const unstableByAngle = Math.abs(x) >= 20 || Math.abs(y) >= 30 || Math.abs(z) >= 20;
        const unstableByPosition = !['center', ''].includes(pos);
        if (unstableByAngle || unstableByPosition) return 'unstable';

        return 'none';
    }, [head.angle_x, head.angle_y, head.angle_z, head.position, head.source]);

    const analytics = useMemo(() => {
        const fallback = {
            avgConfidence: 0,
            alertLoadPct: 0,
            transitions: 0,
            stabilityScore: 0,
            driftLabel: 'Stable',
            driftTone: 'neutral',
            lastUpdate: null,
            windowSize: 0,
        };

        if (!trendPredictions.length) return fallback;

        const tones = trendPredictions.map((pred) => getStatusTone(pred.status));
        const confidences = trendPredictions.map((pred) => Math.round((pred.confidence || 0) * 100));
        const riskScores = tones.map((tone) => (tone === 'danger' ? 3 : tone === 'warning' ? 2 : 1));

        const transitions = tones.slice(1).reduce((count, tone, idx) => {
            return count + (tone !== tones[idx] ? 1 : 0);
        }, 0);

        const alertLoadPct = Math.round((tones.filter((tone) => tone !== 'safe').length / tones.length) * 100);
        const avgConfidence = Math.round(confidences.reduce((sum, val) => sum + val, 0) / confidences.length);

        const maxConf = Math.max(...confidences);
        const minConf = Math.min(...confidences);
        const volatility = maxConf - minConf;
        const stabilityScore = Math.max(5, Math.min(99, Math.round(100 - volatility * 1.05 - transitions * 3.2)));

        const recentRisk = riskScores.slice(-6);
        const previousRisk = riskScores.slice(-12, -6);
        const avgRecentRisk = recentRisk.length ? recentRisk.reduce((s, v) => s + v, 0) / recentRisk.length : 1;
        const avgPreviousRisk = previousRisk.length ? previousRisk.reduce((s, v) => s + v, 0) / previousRisk.length : avgRecentRisk;
        const riskDelta = avgRecentRisk - avgPreviousRisk;

        let driftLabel = 'Stable';
        let driftTone = 'neutral';
        if (riskDelta > 0.18) {
            driftLabel = 'Rising';
            driftTone = 'warning';
        } else if (riskDelta < -0.18) {
            driftLabel = 'Improving';
            driftTone = 'safe';
        }

        return {
            avgConfidence,
            alertLoadPct,
            transitions,
            stabilityScore,
            driftLabel,
            driftTone,
            lastUpdate: recentPredictions[0]?.time || null,
            windowSize: trendPredictions.length,
        };
    }, [recentPredictions, trendPredictions]);

    return (
        <div className="vehicle-ops-shell">
            <section className="vehicle-ops-main">
                <div className="vehicle-metric-rack">
                    <div className={`vehicle-metric tone-${connectionMeta.tone}`}>
                        <span className="vehicle-metric-label"><Waves size={14} /> Link</span>
                        <span className="vehicle-metric-value">{connectionMeta.label}</span>
                    </div>

                    <div className={`vehicle-metric tone-${perclosTone}`}>
                        <span className="vehicle-metric-label">PERCLOS</span>
                        <span className="vehicle-metric-value">{perclosPct}%</span>
                    </div>

                    <div className="vehicle-metric tone-neutral">
                        <span className="vehicle-metric-label">EAR</span>
                        <span className="vehicle-metric-value">{(perclos.ear || 0).toFixed(2)}</span>
                    </div>

                    <div className="vehicle-metric tone-neutral">
                        <span className="vehicle-metric-label">MAR</span>
                        <span className="vehicle-metric-value">{(perclos.mar || 0).toFixed(2)}</span>
                    </div>

                    <div className="vehicle-metric tone-neutral">
                        <span className="vehicle-metric-label"><Clock3 size={14} /> Confidence</span>
                        <span className="vehicle-metric-value">{confidencePct}%</span>
                    </div>
                </div>

                <div className="vehicle-ops-content">
                    <div className="vehicle-stage-column">
                        <div className="vehicle-panel vehicle-panel-camera">
                            <div className="vehicle-panel-header">
                                <span className="vehicle-panel-title"><Camera size={17} /> Driver Camera Feed</span>
                            </div>
                            <div className="vehicle-panel-body no-pad">
                                <CameraModule vehicleOverlayMode={cameraOverlayMode} />
                            </div>
                        </div>

                        <div className="vehicle-panel vehicle-panel-timeline">
                            <div className="vehicle-panel-header">
                                <span className="vehicle-panel-title"><Radio size={17} /> Driver Stability Analytics</span>
                            </div>
                            <div className="vehicle-panel-body vehicle-history-body">
                                {hasPerclosData ? (
                                    recentPredictions.length > 0 ? (
                                        <div className="vehicle-insight-wrap">
                                            <div className="vehicle-insight-stats vehicle-analytics-grid">
                                                <div className={`vehicle-insight-card tone-${analytics.driftTone}`}>
                                                    <span className="vehicle-insight-label">Risk Drift</span>
                                                    <strong>{analytics.driftLabel}</strong>
                                                </div>
                                                <div className={`vehicle-insight-card tone-${analytics.alertLoadPct > 45 ? 'danger' : analytics.alertLoadPct > 20 ? 'warning' : 'safe'}`}>
                                                    <span className="vehicle-insight-label">Alert Load</span>
                                                    <strong>{analytics.alertLoadPct}%</strong>
                                                </div>
                                                <div className="vehicle-insight-card tone-neutral">
                                                    <span className="vehicle-insight-label">State Shifts</span>
                                                    <strong>{analytics.transitions}</strong>
                                                </div>
                                                <div className="vehicle-insight-card tone-neutral">
                                                    <span className="vehicle-insight-label">Stability</span>
                                                    <strong>{analytics.stabilityScore}%</strong>
                                                </div>
                                            </div>

                                            <div className="vehicle-signal-board">
                                                <div className="vehicle-signal-row">
                                                    <div className="vehicle-signal-head">
                                                        <span>Confidence Track</span>
                                                        <strong>{analytics.avgConfidence}% avg</strong>
                                                    </div>
                                                    <div className="vehicle-confidence-trend">
                                                        {trendPredictions.map((pred, idx) => {
                                                            const confidence = Math.max(5, Math.min(100, Math.round((pred.confidence || 0) * 100)));
                                                            const tone = confidence >= 75 ? 'safe' : confidence >= 45 ? 'warning' : 'danger';

                                                            return (
                                                                <div
                                                                    key={`${pred.time}-conf-${idx}`}
                                                                    className={`vehicle-trend-bar tone-${tone}`}
                                                                    style={{ height: `${confidence}%` }}
                                                                    title={`Confidence ${confidence}%`}
                                                                />
                                                            );
                                                        })}
                                                    </div>
                                                </div>

                                                <div className="vehicle-signal-row">
                                                    <div className="vehicle-signal-head">
                                                        <span>Risk Oscillation</span>
                                                        <strong>{analytics.windowSize} samples</strong>
                                                    </div>
                                                    <div className="vehicle-risk-trend">
                                                        {trendPredictions.map((pred, idx) => {
                                                            const tone = getStatusTone(pred.status);
                                                            const riskHeight = tone === 'danger' ? 92 : tone === 'warning' ? 62 : 34;

                                                            return (
                                                                <div
                                                                    key={`${pred.time}-risk-${idx}`}
                                                                    className={`vehicle-trend-bar tone-${tone}`}
                                                                    style={{ height: `${riskHeight}%` }}
                                                                    title={`Risk ${pred.status || 'Unknown'}`}
                                                                />
                                                            );
                                                        })}
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="vehicle-ops-note">
                                                <span>Window: last {analytics.windowSize} inference frames</span>
                                                <span>
                                                    Last update: {analytics.lastUpdate ? new Date(analytics.lastUpdate).toLocaleTimeString() : 'N/A'}
                                                </span>
                                            </div>
                                        </div>
                                    ) : (
                                        <EmptyState message="Waiting for predictions..." />
                                    )
                                ) : isLoading ? (
                                    <EmptyState message="Preparing timeline..." loading />
                                ) : (
                                    <EmptyState message="No prediction history available" />
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="vehicle-insights-column">
                        <div className="vehicle-panel">
                            <div className="vehicle-panel-header">
                                <span className="vehicle-panel-title"><Eye size={17} /> Eye Behavior Model</span>
                                <span className={`vehicle-chip tone-${perclosTone}`}>{riskBand}</span>
                            </div>
                            <div className="vehicle-panel-body vehicle-eye-body">
                                {hasPerclosData ? (
                                    <EyeModel3D
                                        perclos={vehicleData.perclos.perclos || 0}
                                        ear={vehicleData.perclos.ear || 0.3}
                                        status={vehicleData.perclos.status || 'Open'}
                                    />
                                ) : isLoading ? (
                                    <EmptyState message="Initializing eye model..." loading />
                                ) : (
                                    <EmptyState message="No eye data available" />
                                )}
                            </div>
                        </div>

                        <div className="vehicle-panel">
                            <div className="vehicle-panel-header">
                                <span className="vehicle-panel-title"><Radar size={17} /> Head Position Stability</span>
                                <span className="vehicle-chip tone-neutral">{headPosition}</span>
                            </div>
                            <div className="vehicle-panel-body">
                                {hasHeadData ? (
                                    <HeadPositionChart data={headPositionHistory} />
                                ) : (
                                    <EmptyState message="Collecting head motion data..." />
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <aside className="vehicle-ops-side">
                <div className="vehicle-panel vehicle-command-panel">
                    <div className="vehicle-panel-header">
                        <span className="vehicle-panel-title"><Gauge size={17} /> Driver Command Status</span>
                    </div>
                    <div className="vehicle-panel-body no-pad">
                        <VehicleStatus />
                    </div>
                </div>
            </aside>
        </div>
    );
};

export default VehicleDashboard;
