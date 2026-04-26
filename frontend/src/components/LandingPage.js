import React from "react";
import { BrainCircuit, Car, ShieldCheck, Settings, ArrowRight, UserCheck } from "lucide-react";
import { useUserContext } from "../context/UserContext";
import "./Css/LandingPage.css";

export default function LandingPage({ onSelectMode }) {
  const { userProfile } = useUserContext();

  return (
    <div className="landing-container">
      <div className="landing-header" style={{ textAlign: 'center', marginBottom: '40px' }}>
        <div style={{ 
          background: 'rgba(59, 130, 246, 0.1)', 
          width: '72px', 
          height: '72px', 
          borderRadius: '22px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          margin: '0 auto 24px',
          border: '1px solid rgba(59, 130, 246, 0.3)'
        }}>
          <BrainCircuit size={36} color="#60a5fa" />
        </div>
        <h1 style={{ fontSize: '3rem', fontWeight: '900', marginBottom: '8px', letterSpacing: '-0.03em' }}>FatigueGuard AI</h1>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '20px' }}>
           <div style={{ padding: '4px 12px', background: 'rgba(16, 185, 129, 0.15)', color: '#10b981', borderRadius: '999px', fontSize: '0.75rem', fontWeight: '700', border: '1px solid rgba(16, 185, 129, 0.2)', display: 'flex', alignItems: 'center', gap: '6px' }}>
             <UserCheck size={12} /> ACTIVE PROFILE: {userProfile.name} ({userProfile.company})
           </div>
        </div>
        <p style={{ color: '#94a3b8', fontSize: '1.1rem', maxWidth: '550px', lineHeight: '1.6' }}>
          Next-generation fatigue monitoring for enterprise fleets. 
          Choose a standalone module to initialize security protocols.
        </p>
      </div>

      <div className="mode-grid">
        {/* Standard Model */}
        <div className="mode-card" onClick={() => onSelectMode('standard')}>
          <div className="mode-icon-box" style={{ color: '#6366f1', background: 'rgba(99, 102, 241, 0.15)', width: '52px', height: '52px', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '24px' }}>
            <BrainCircuit size={28} />
          </div>
          <h3 style={{ fontSize: '1.4rem', fontWeight: '800', marginBottom: '12px' }}>Standard Model</h3>
          <p style={{ fontSize: '0.95rem', color: '#94a3b8', lineHeight: '1.6', marginBottom: '32px', flexGrow: 1 }}>
            General purpose AI monitoring. Ideal for desktop, workspace, or static security environments. 
          </p>
          <div className="mode-footer" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#6366f1', fontWeight: '700', fontSize: '0.9rem' }}>
            <span>Initialize Engine</span>
            <ArrowRight size={18} />
          </div>
        </div>

        {/* Vehicle Model */}
        <div className="mode-card" onClick={() => onSelectMode('vehicle')}>
          <div className="mode-icon-box" style={{ color: '#f59e0b', background: 'rgba(245, 158, 11, 0.15)', width: '52px', height: '52px', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '24px' }}>
            <Car size={28} />
          </div>
          <h3 style={{ fontSize: '1.4rem', fontWeight: '800', marginBottom: '12px' }}>Vehicle Model</h3>
          <p style={{ fontSize: '0.95rem', color: '#94a3b8', lineHeight: '1.6', marginBottom: '32px', flexGrow: 1 }}>
            Driver-centric monitoring. Hardware-aware head pose correction and low-latency facial mesh processing.
          </p>
          <div className="mode-footer" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#f59e0b', fontWeight: '700', fontSize: '0.9rem' }}>
            <span>Initialize Engine</span>
            <ArrowRight size={18} />
          </div>
        </div>

        {/* Owner App */}
        <div className="mode-card" onClick={() => onSelectMode('owner')}>
          <div className="mode-icon-box" style={{ color: '#10b981', background: 'rgba(16, 185, 129, 0.15)', width: '52px', height: '52px', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '24px' }}>
            <ShieldCheck size={28} />
          </div>
          <h3 style={{ fontSize: '1.4rem', fontWeight: '800', marginBottom: '12px' }}>Owner App</h3>
          <p style={{ fontSize: '0.95rem', color: '#94a3b8', lineHeight: '1.6', marginBottom: '32px', flexGrow: 1 }}>
            Admin operations center. Live synchronization with Cloud APIs to monitor fleet-wide safety and sensor health.
          </p>
          <div className="mode-footer" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#10b981', fontWeight: '700', fontSize: '0.9rem' }}>
            <span>Open Command Center</span>
            <ArrowRight size={18} />
          </div>
        </div>
      </div>

      <div style={{ marginTop: '60px', color: '#475569', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <Settings size={14} />
        <span style={{ letterSpacing: '0.05em', fontWeight: '600' }}>V1.0.2 • CLOUD SYNCHRONIZED ARCHITECTURE</span>
      </div>
    </div>
  );
}
