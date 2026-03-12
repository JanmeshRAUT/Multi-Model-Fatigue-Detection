import React, { useEffect, useRef, useState } from 'react';
import { useVehicleContext } from '../context/VehicleContext';
import '../Dashboard.css';
import { Compass, Eye, Activity, Radio, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import HeadPositionChart from './HeadPositionChart';
import VehicleStatus from './VehicleStatus';
import CameraModule from './CameraModule';
import EyeModel3D from './EyeModel3D';

const VehicleDashboard = () => {
    const { vehicleData, headPositionHistory, predictionHistory } = useVehicleContext();
    const wsRef = useRef(null);
    const [isLoading, setIsLoading] = useState(true);
    
    // Track when data arrives
    useEffect(() => {
        if (vehicleData) {
            setIsLoading(false);
        }
    }, [vehicleData]);

    // --- WebSocket Setup ---
    useEffect(() => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/vehicle/detect`;

        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
            console.log("[VehicleDashboard] WebSocket Connected");
        };

        wsRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("[VehicleDashboard] WebSocket Data:", data);
        };

        wsRef.current.onerror = (error) => {
            console.error("[VehicleDashboard] WebSocket Error:", error);
        };

        wsRef.current.onclose = () => {
            console.log("[VehicleDashboard] WebSocket Closed");
        };

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    return (
        <div className="grid-container">
            {/* Left Column: Data Charts */}
            <section className="charts-section">
                
                {/* Row 1: 3D Eyes Model & Metrics */}
                <div className="charts-row-1">
                    <div className="card">
                        <div className="card-header">
                            <span className="card-title"><Eye size={18} className="card-icon"/> Eye Status 3D View</span>
                        </div>
                        <div className="chart-body-fill" style={{ padding: '8px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                            {vehicleData && vehicleData.perclos ? (
                                <EyeModel3D 
                                    perclos={vehicleData.perclos.perclos || 0}
                                    ear={vehicleData.perclos.ear || 0.3}
                                    status={vehicleData.perclos.status || "Open"}
                                />
                            ) : isLoading ? (
                                <div style={{ textAlign: 'center', color: '#94a3b8', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <div style={{ textAlign: 'center' }}>
                                        <Loader size={32} style={{ margin: '0 auto 8px', opacity: 0.6, animation: 'spin 2s linear infinite' }} />
                                        <div style={{ fontSize: '0.9rem' }}>Initializing Camera...</div>
                                    </div>
                                </div>
                            ) : (
                                <div style={{ textAlign: 'center', color: '#94a3b8', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <div style={{ textAlign: 'center' }}>
                                        <AlertCircle size={32} style={{ margin: '0 auto 8px', opacity: 0.5, color: '#f59e0b' }} />
                                        <div style={{ fontSize: '0.9rem' }}>Waiting for Data...</div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="card">
                        <div className="card-header">
                            <span className="card-title"><Eye size={18} className="card-icon"/> Vision Metrics</span>
                        </div>
                        <div className="chart-body-fill" style={{ padding: '12px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                            {vehicleData && vehicleData.perclos ? (
                                <>
                                    <div style={{ padding: '12px', background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)', borderRadius: '8px', border: '2px solid #f59e0b', textAlign: 'center' }}>
                                        <p style={{ fontSize: '0.75rem', color: '#92400e', margin: 0, fontWeight: 600, marginBottom: '4px' }}>EYE CLOSURE</p>
                                        <p style={{ fontSize: '1.8rem', fontWeight: 900, color: '#d97706', margin: 0 }}>{((vehicleData.perclos.perclos || 0)).toFixed(1)}%</p>
                                    </div>

                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                                        <div style={{ padding: '10px', background: (vehicleData.perclos.ear || 0) > 0.25 ? '#dcfce7' : '#fee2e2', borderRadius: '6px', textAlign: 'center', border: `2px solid ${(vehicleData.perclos.ear || 0) > 0.25 ? '#10b981' : '#ef4444'}` }}>
                                            <p style={{ fontSize: '0.7rem', color: '#374151', margin: 0, fontWeight: 600 }}>EAR</p>
                                            <p style={{ fontSize: '1.3rem', fontWeight: 800, color: '#1f2937', margin: '4px 0 0' }}>{((vehicleData.perclos.ear || 0).toFixed(2))}</p>
                                        </div>
                                        <div style={{ padding: '10px', background: (vehicleData.perclos.mar || 0) > 0.25 ? '#dbeafe' : '#fee2e2', borderRadius: '6px', textAlign: 'center', border: `2px solid ${(vehicleData.perclos.mar || 0) > 0.25 ? '#3b82f6' : '#ef4444'}` }}>
                                            <p style={{ fontSize: '0.7rem', color: '#374151', margin: 0, fontWeight: 600 }}>MAR</p>
                                            <p style={{ fontSize: '1.3rem', fontWeight: 800, color: '#1f2937', margin: '4px 0 0' }}>{((vehicleData.perclos.mar || 0).toFixed(2))}</p>
                                        </div>
                                    </div>

                                    <div style={{ padding: '10px', background: vehicleData.perclos.status === 'Open' ? 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)' : 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)', borderRadius: '6px', textAlign: 'center', border: `2px solid ${vehicleData.perclos.status === 'Open' ? '#10b981' : '#dc2626'}`, fontWeight: 700, fontSize: '0.9rem', color: vehicleData.perclos.status === 'Open' ? '#166534' : '#7f1d1d' }}>
                                        {vehicleData.perclos.status === 'Open' ? '✓ Eyes Open' : '✕ Eyes Closed'}
                                    </div>
                                </>
                            ) : isLoading ? (
                                <div style={{ textAlign: 'center', color: '#94a3b8', padding: '24px 0' }}>
                                    <Loader size={24} style={{ margin: '0 auto 8px', animation: 'spin 2s linear infinite' }} />
                                    <p style={{ margin: 0, fontSize: '0.9rem' }}>Scanning...</p>
                                </div>
                            ) : (
                                <div style={{ textAlign: 'center', color: '#94a3b8', padding: '24px 0' }}>
                                    <AlertCircle size={24} style={{ margin: '0 auto 8px', color: '#f59e0b' }} />
                                    <p style={{ margin: 0, fontSize: '0.9rem' }}>No data</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Row 2: Charts */}
                <div className="charts-row-2">
                    <div className="card">
                        <div className="card-header">
                            <span className="card-title"><Activity size={18} className="card-icon"/> Head Position Trends</span>
                        </div>
                        <div className="chart-body-fill">
                            {headPositionHistory.length > 0 ? (
                                <HeadPositionChart data={headPositionHistory} />
                            ) : (
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#94a3b8' }}>
                                    Collecting data...
                                </div>
                            )}
                        </div>
                    </div>
                    
                    <div className="card">
                        <div className="card-header">
                            <span className="card-title"><Radio size={18} className="card-icon"/> Prediction History</span>
                        </div>
                        <div className="chart-body-fill" style={{ padding: '12px', overflowY: 'auto', maxHeight: '280px' }}>
                            {predictionHistory && predictionHistory.length > 0 ? (
                                <div style={{ fontSize: '0.85rem' }}>
                                    {predictionHistory.slice(-8).reverse().map((pred, idx) => {
                                        const isSafe = pred.status === 'Alert';
                                        const isDrowsy = pred.status === 'Drowsy';
                                        const isFatigued = pred.status === 'Fatigued';
                                        
                                        const bgGradient = isFatigued 
                                            ? 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)'
                                            : isDrowsy 
                                            ? 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)'
                                            : 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)';
                                        
                                        const borderColor = isFatigued ? '#dc2626' : isDrowsy ? '#f59e0b' : '#10b981';
                                        const textColor = isFatigued ? '#7f1d1d' : isDrowsy ? '#92400e' : '#166534';
                                        const statusIcon = isFatigued ? '🚨' : isDrowsy ? '⚠️' : '✓';
                                        const statusText = isFatigued ? 'Fatigued' : isDrowsy ? 'Drowsy' : 'Alert';
                                        
                                        return (
                                            <div 
                                                key={idx} 
                                                style={{ 
                                                    marginBottom: '10px', 
                                                    padding: '12px', 
                                                    background: bgGradient,
                                                    borderLeft: `4px solid ${borderColor}`,
                                                    borderRadius: '8px',
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center',
                                                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.08)',
                                                    transition: 'all 0.2s ease'
                                                }}
                                            >
                                                <div>
                                                    <p style={{ margin: '0 0 4px', fontWeight: 700, color: textColor, fontSize: '0.95rem' }}>
                                                        {statusIcon} {statusText}
                                                    </p>
                                                    {pred.microsleep && (
                                                        <p style={{ margin: 0, fontSize: '0.7rem', color: '#dc2626', fontWeight: 700 }}>
                                                            MICROSLEEP ALERT!
                                                        </p>
                                                    )}
                                                </div>
                                                <div style={{ textAlign: 'right' }}>
                                                    <p style={{ margin: '0 0 2px', fontSize: '1.2rem', fontWeight: 900, color: '#1f2937' }}>
                                                        {((pred.confidence || 0) * 100).toFixed(0)}%
                                                    </p>
                                                    <p style={{ margin: 0, fontSize: '0.65rem', color: '#6b7280' }}>
                                                        confidence
                                                    </p>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : isLoading ? (
                                <div style={{ textAlign: 'center', color: '#94a3b8', padding: '30px 0' }}>
                                    <Loader size={24} style={{ margin: '0 auto 8px', animation: 'spin 2s linear infinite', opacity: 0.6 }} />
                                    <p style={{ margin: 0, fontSize: '0.9rem' }}>Building history...</p>
                                </div>
                            ) : (
                                <div style={{ textAlign: 'center', color: '#94a3b8', padding: '30px 0' }}>
                                    <Radio size={24} style={{ margin: '0 auto 8px', opacity: 0.5, color: '#cbd5e1' }} />
                                    <p style={{ margin: 0, fontSize: '0.9rem' }}>Waiting for predictions</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

            </section>

            {/* Right Column: Camera & Status */}
            <aside className="side-panel">
                
                {/* Live Camera Feed */}
                <div className="card camera-card">
                    <CameraModule />
                </div>

                {/* Vehicle Status Widget */}
                <div className="card fatigue-card">
                    <VehicleStatus />
                </div>

            </aside>

        </div>
    );
};

export default VehicleDashboard;
