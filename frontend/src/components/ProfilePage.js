import React, { useState } from "react";
import { User, Truck, Car, Save, ArrowLeft, Building2, BadgeCheck } from "lucide-react";
import { useUserContext } from "../context/UserContext";
import "./Css/OwnerDashboard.css"; // Reuse existing owner styles for consistency

export default function ProfilePage({ onBack }) {
  const { userProfile, updateProfile } = useUserContext();
  const [formData, setFormData] = useState({ ...userProfile });
  const [saveStatus, setSaveStatus] = useState(null);

  const handleSave = () => {
    updateProfile(formData);
    setSaveStatus("Profile Updated Successfully!");
    setTimeout(() => setSaveStatus(null), 3000);
  };

  return (
    <div className="owner-dashboard">
      <section className="owner-hero">
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button 
            onClick={onBack}
            style={{ background: 'transparent', border: 'none', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
          >
            <ArrowLeft size={24} />
          </button>
          <div>
            <div className="owner-kicker">USER SETTINGS</div>
            <h2 className="owner-title">Owner Profile & Vehicle Configuration</h2>
            <p className="owner-subtitle">Manage your credentials and fleet settings for Cloud synchronization.</p>
          </div>
        </div>
      </section>

      <div className="owner-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', marginTop: '20px' }}>
        {/* Profile Card */}
        <div className="owner-panel">
          <h3 style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '12px', marginBottom: '16px' }}>
            <User size={18} /> Personal Information
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '0.75rem', fontWeight: '700', color: '#64748b' }}>FULL NAME</label>
              <input 
                className="owner-vehicle-select"
                style={{ width: '100%', padding: '10px' }}
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '0.75rem', fontWeight: '700', color: '#64748b' }}>COMPANY NAME</label>
              <div style={{ position: 'relative' }}>
                 <Building2 size={14} style={{ position: 'absolute', left: '10px', top: '12px', color: '#94a3b8' }} />
                 <input 
                    className="owner-vehicle-select"
                    style={{ width: '100%', padding: '10px 10px 10px 32px' }}
                    value={formData.company}
                    onChange={(e) => setFormData({...formData, company: e.target.value})}
                  />
              </div>
            </div>
          </div>
        </div>

        {/* Fleet Configuration */}
        <div className="owner-panel">
          <h3 style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '12px', marginBottom: '16px' }}>
            <Truck size={18} /> Fleet Settings
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '0.75rem', fontWeight: '700', color: '#64748b' }}>VEHICLE TYPE</label>
              <div style={{ display: 'flex', gap: '10px', marginTop: '4px' }}>
                <button 
                  onClick={() => setFormData({...formData, vehicleType: 'Car'})}
                  style={{ 
                    flex: 1, 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    gap: '8px',
                    padding: '12px',
                    borderRadius: '8px',
                    border: formData.vehicleType === 'Car' ? '2px solid #3b82f6' : '1px solid #e2e8f0',
                    background: formData.vehicleType === 'Car' ? '#eff6ff' : 'white',
                    color: formData.vehicleType === 'Car' ? '#1e40af' : '#64748b',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                >
                  <Car size={18} /> Car
                </button>
                <button 
                   onClick={() => setFormData({...formData, vehicleType: 'Truck'})}
                   style={{ 
                    flex: 1, 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    gap: '8px',
                    padding: '12px',
                    borderRadius: '8px',
                    border: formData.vehicleType === 'Truck' ? '2px solid #3b82f6' : '1px solid #e2e8f0',
                    background: formData.vehicleType === 'Truck' ? '#eff6ff' : 'white',
                    color: formData.vehicleType === 'Truck' ? '#1e40af' : '#64748b',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                >
                  <Truck size={18} /> Truck
                </button>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '0.75rem', fontWeight: '700', color: '#64748b' }}>VEHICLE IDENTIFIER</label>
              <div style={{ position: 'relative' }}>
                 <BadgeCheck size={14} style={{ position: 'absolute', left: '10px', top: '12px', color: '#94a3b8' }} />
                 <input 
                    className="owner-vehicle-select"
                    style={{ width: '100%', padding: '10px 10px 10px 32px' }}
                    value={formData.vehicleId}
                    onChange={(e) => setFormData({...formData, vehicleId: e.target.value})}
                  />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
         {saveStatus && <span style={{ color: '#10b981', fontWeight: '600', marginRight: '16px', display: 'flex', alignItems: 'center' }}>{saveStatus}</span>}
         <button 
          onClick={handleSave}
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px', 
            padding: '12px 24px', 
            background: '#0f172a', 
            color: 'white', 
            border: 'none', 
            borderRadius: '12px', 
            fontWeight: '700',
            cursor: 'pointer',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
          }}
         >
           <Save size={18} /> Save Profile
         </button>
      </div>
    </div>
  );
}
