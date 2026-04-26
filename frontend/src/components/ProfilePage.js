import React, { useState } from "react";
import { User, Truck, Car, Save, ArrowLeft, Building2, BadgeCheck } from "lucide-react";
import { useUserContext } from "../context/UserContext";
import "./Css/OwnerDashboard.css"; // Reuse existing owner styles for consistency

export default function ProfilePage({ onBack }) {
  const { userProfile, updateProfile } = useUserContext();
  const [formData, setFormData] = useState({ ...userProfile });
  const [saveStatus, setSaveStatus] = useState(null);

  const handleSaveAndLaunch = () => {
    updateProfile(formData);
    onBack();
  };

  return (
    <div className="owner-dashboard" style={{ padding: '24px', background: '#f8fafc', minHeight: '100vh' }}>
      <section className="owner-hero" style={{ marginBottom: '32px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <button 
            onClick={onBack}
            className="exit-btn"
            style={{ padding: '10px' }}
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <div className="owner-kicker" style={{ color: '#93c5fd' }}>SYSTEM CONFIGURATION</div>
            <h2 className="owner-title" style={{ fontSize: '1.75rem' }}>Fleet & Security Profile</h2>
            <p className="owner-subtitle" style={{ fontSize: '0.95rem' }}>Configure your unique Vehicle ID and Owner credentials for Cloud synchronization.</p>
          </div>
        </div>
      </section>

      <div className="owner-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
        {/* Profile Card */}
        <div className="owner-panel" style={{ padding: '24px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}>
          <h3 style={{ borderBottom: '1px solid #f1f5f9', paddingBottom: '16px', marginBottom: '24px', fontSize: '1.1rem', fontWeight: '800' }}>
            <User size={20} color="#3b82f6" /> Identity Management
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.7rem', fontWeight: '800', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Full Legal Name</label>
              <input 
                className="owner-vehicle-select"
                style={{ width: '100%', padding: '12px', fontSize: '0.95rem', background: '#f1f5f9', border: '1px solid #e2e8f0' }}
                placeholder="e.g. Janmesh Raut"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.7rem', fontWeight: '800', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Fleet Company</label>
              <div style={{ position: 'relative' }}>
                 <Building2 size={16} style={{ position: 'absolute', left: '12px', top: '14px', color: '#94a3b8' }} />
                 <input 
                    className="owner-vehicle-select"
                    style={{ width: '100%', padding: '12px 12px 12px 40px', fontSize: '0.95rem', background: '#f1f5f9', border: '1px solid #e2e8f0' }}
                    placeholder="e.g. Logistics Pro Solutions"
                    value={formData.company}
                    onChange={(e) => setFormData({...formData, company: e.target.value})}
                  />
              </div>
            </div>
          </div>
        </div>

        {/* Fleet Configuration */}
        <div className="owner-panel" style={{ padding: '24px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}>
          <h3 style={{ borderBottom: '1px solid #f1f5f9', paddingBottom: '16px', marginBottom: '24px', fontSize: '1.1rem', fontWeight: '800' }}>
            <Truck size={20} color="#10b981" /> Fleet Deployment
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.7rem', fontWeight: '800', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Assigned Vehicle Class</label>
              <div style={{ display: 'flex', gap: '12px', marginTop: '4px' }}>
                <button 
                  onClick={() => setFormData({...formData, vehicleType: 'Car'})}
                  style={{ 
                    flex: 1, 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    gap: '10px',
                    padding: '16px',
                    borderRadius: '12px',
                    border: formData.vehicleType === 'Car' ? '2px solid #3b82f6' : '1px solid #e2e8f0',
                    background: formData.vehicleType === 'Car' ? '#eff6ff' : 'white',
                    color: formData.vehicleType === 'Car' ? '#1e40af' : '#64748b',
                    cursor: 'pointer',
                    fontWeight: '700',
                    transition: 'all 0.2s'
                  }}
                >
                  <Car size={20} /> Car
                </button>
                <button 
                   onClick={() => setFormData({...formData, vehicleType: 'Truck'})}
                   style={{ 
                    flex: 1, 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    gap: '10px',
                    padding: '16px',
                    borderRadius: '12px',
                    border: formData.vehicleType === 'Truck' ? '2px solid #3b82f6' : '1px solid #e2e8f0',
                    background: formData.vehicleType === 'Truck' ? '#eff6ff' : 'white',
                    color: formData.vehicleType === 'Truck' ? '#1e40af' : '#64748b',
                    cursor: 'pointer',
                    fontWeight: '700',
                    transition: 'all 0.2s'
                  }}
                >
                  <Truck size={20} /> Truck
                </button>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label style={{ fontSize: '0.7rem', fontWeight: '800', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Unique Vehicle ID (Used for Data Ingest)</label>
              <div style={{ position: 'relative' }}>
                 <BadgeCheck size={16} style={{ position: 'absolute', left: '12px', top: '14px', color: '#94a3b8' }} />
                 <input 
                    className="owner-vehicle-select"
                    style={{ width: '100%', padding: '12px 12px 12px 40px', fontSize: '0.95rem', background: '#f1f5f9', border: '1px solid #e2e8f0' }}
                    placeholder="e.g. TRUCK-770-PRO"
                    value={formData.vehicleId}
                    onChange={(e) => setFormData({...formData, vehicleId: e.target.value})}
                  />
              </div>
              <p style={{ fontSize: '0.7rem', color: '#94a3b8', marginTop: '4px' }}>
                Note: This ID must match the <code>VEHICLE_ID</code> in your local <code>bridge.py</code> script.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '16px', marginTop: '32px' }}>
         {saveStatus && <span style={{ color: '#10b981', fontWeight: '700', fontSize: '0.9rem' }}>{saveStatus}</span>}
         <button 
          onClick={handleSave}
          style={{ 
            padding: '12px 20px', 
            background: 'white', 
            color: '#0f172a', 
            border: '1px solid #e2e8f0', 
            borderRadius: '12px', 
            fontWeight: '600',
            cursor: 'pointer'
          }}
         >
           Save Changes
         </button>
         <button 
          onClick={handleSaveAndLaunch}
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '10px', 
            padding: '14px 32px', 
            background: 'linear-gradient(135deg, #0f172a, #1e293b)', 
            color: 'white', 
            border: 'none', 
            borderRadius: '12px', 
            fontWeight: '800',
            cursor: 'pointer',
            boxShadow: '0 10px 15px -3px rgba(59, 130, 246, 0.2)'
          }}
         >
           Save & Launch Application <ArrowRight size={18} />
         </button>
      </div>
    </div>
  );
}
