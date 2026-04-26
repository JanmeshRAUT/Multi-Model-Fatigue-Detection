import React, { useEffect, useState } from "react";
import "./Dashboard.css";
import { 
  Activity, 
  Thermometer, 
  BrainCircuit, 
  User,
  Heart
} from "lucide-react";

// Context
import { FatigueProvider } from "./context/FatigueContext";
import { VehicleProvider, useVehicleContext } from "./context/VehicleContext";
import { ThemeProvider } from "./context/ThemeContext";
import { ModeProvider } from "./context/ModeContext";
import { UserProvider, useUserContext } from "./context/UserContext";

// Components
import BodyTemperatureChart from "./components/BodyTemperatureChart";
import HeartRateChart from "./components/HeartRateChart";
import HRVChart from "./components/HRVChart";
import HeadPositionChart from "./components/HeadPositionChart";
import CameraModule from "./components/CameraModule";
import FatigueStatus from "./components/FatigueStatus";
import ThemeToggle from "./components/ThemeToggle";
import VehicleDashboard from "./components/VehicleDashboard";
import OwnerDashboard from "./components/OwnerDashboard";
import ProfilePage from "./components/ProfilePage";
import LandingPage from "./components/LandingPage";
import { useFatigueData } from "./hooks/useFatigueData";
import { LogOut } from "lucide-react";
import "./components/Css/LandingPage.css";

// Wrapper Component to access Context for Theme
const StandardModelWithSwitcher = ({ setShowProfile, onExit }) => {
  return (
    <DashboardContent 
      setShowProfile={setShowProfile}
      onExit={onExit}
    />
  );
};

// Vehicle Model Wrapper
const VehicleModelWithSwitcher = ({ setShowProfile, onExit }) => {
  return (
    <VehicleDashboardWithHeader 
      setShowProfile={setShowProfile}
      onExit={onExit}
    />
  );
};

const OwnerModelWithSwitcher = ({ setShowProfile, onExit }) => {
  return (
    <OwnerDashboardWithHeader 
      setShowProfile={setShowProfile}
      onExit={onExit}
    />
  );
};

// Common Header Content (Standalone Mode)
const HeaderContent = ({ statusLabel, setShowProfile, onExit }) => {
  const { userProfile } = useUserContext();
  
  return (
    <>
      <div className="brand">
        <div className="brand-logo">
          <BrainCircuit size={20} />
        </div>
        <span className="brand-name">FatigueGuard Pro</span>
      </div>
      
      <div className="header-actions">
        <div className="status-badge">
          <span className="live-dot"></span>
          {statusLabel}
        </div>
        
        <ThemeToggle />

        <button 
          onClick={onExit}
          className="exit-btn"
          title="Return to Menu"
        >
          <LogOut size={16} />
          <span>Exit Module</span>
        </button>
        
        <button 
          onClick={() => setShowProfile(true)}
          className="user-profile-btn"
          title={`Profile Settings: ${userProfile.name}`}
          style={{
            width: 32, 
            height: 32, 
            borderRadius: '50%', 
            background: '#e2e8f0', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            border: 'none',
            cursor: 'pointer',
            padding: 0
          }}
        >
          <User size={16} color="#64748b" />
        </button>
      </div>
    </>
  );
};

// Vehicle Dashboard with Header
const VehicleDashboardWithHeader = ({ setShowProfile, onExit }) => {
  const { vehicleData } = useVehicleContext();
  
  const predictedStatus = vehicleData?.prediction?.status || "Unknown";
  const themeClass = 
    predictedStatus === "Fatigued" ? "theme-danger" : 
    (predictedStatus === "Drowsy" ? "theme-warning" : "theme-safe");

  return (
    <div className={`dashboard-container ${themeClass}`}>
      <header className="top-header">
        <HeaderContent 
          statusLabel="Vehicle Engine Active"
          setShowProfile={setShowProfile}
          onExit={onExit}
        />
      </header>

      <main className="dashboard-content vehicle-content">
        <VehicleDashboard />
      </main>
    </div>
  );
};

const OwnerDashboardWithHeader = ({ setShowProfile, onExit }) => {
  const { ml_fatigue_status } = useFatigueData();

  const themeClass =
    ml_fatigue_status === "Fatigued" ? "theme-danger" :
    (ml_fatigue_status === "Drowsy" ? "theme-warning" : "theme-safe");

  return (
    <div className={`dashboard-container ${themeClass}`}>
      <header className="top-header">
        <HeaderContent 
          statusLabel="Fleet Command Center"
          setShowProfile={setShowProfile}
          onExit={onExit}
        />
      </header>

      <main className="dashboard-content owner-content" style={{ padding: 16 }}>
        <OwnerDashboard />
      </main>
    </div>
  );
};

// Wrapper Component to access Context for Theme
const DashboardContent = ({ setShowProfile, onExit }) => {
  const { ml_fatigue_status } = useFatigueData(); 
  
  const themeClass = 
    ml_fatigue_status === "Fatigued" ? "theme-danger" : 
    (ml_fatigue_status === "Drowsy" ? "theme-warning" : "theme-safe");

  return (
    <div className={`dashboard-container ${themeClass}`}>
      <header className="top-header">
        <HeaderContent 
          statusLabel="Standard AI Monitor"
          setShowProfile={setShowProfile}
          onExit={onExit}
        />
      </header>

      <main className="dashboard-content">
        <div className="grid-container">
          <section className="charts-section">
            <div className="charts-row-1">
              <div className="card">
                <div className="card-header">
                  <span className="card-title"><Heart size={18} className="card-icon"/> Heart Rate</span>
                </div>
                <div className="chart-body-fill">
                   <HeartRateChart />
                </div>
              </div>

              <div className="card">
                <div className="card-header">
                   <span className="card-title"><Thermometer size={18} className="card-icon"/> Temperature</span>
                </div>
                <div className="chart-body-fill">
                   <BodyTemperatureChart />
                </div>
              </div>
            </div>

            <div className="charts-row-2">
               <div className="card">
                  <div className="card-header">
                    <span className="card-title"><Activity size={18} className="card-icon"/> HRV Analysis</span>
                  </div>
                  <div className="chart-body-fill">
                    <HRVChart />
                  </div>
               </div>
               
               <div className="card">
                  <div className="card-header">
                    <span className="card-title"><User size={18} className="card-icon"/> Head Posture</span>
                  </div>
                  <div className="chart-body-fill">
                    <HeadPositionChart />
                  </div>
               </div>
            </div>
          </section>

          <aside className="side-panel">
            <div className="card camera-card">
              <CameraModule />
            </div>

            <div className="card fatigue-card">
               <div className="card-header">
                  <span className="card-title"><BrainCircuit size={18} className="card-icon"/> Fatigue Status</span>
               </div>
               <FatigueStatus />
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
};

function App() {
  const [mounted, setMounted] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null); // null means show selection screen
  const [showProfile, setShowProfile] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSelectMode = (mode) => {
    setSelectedModel(mode);
    setShowProfile(false);
  };

  const handleExit = () => {
    setSelectedModel(null);
    setShowProfile(false);
  };

  if (!mounted) return null;

  return (
    <ThemeProvider>
      <UserProvider>
        <ModeProvider selectedMode={selectedModel === "owner" ? "standard" : (selectedModel || "standard")}>
          {showProfile ? (
            <ProfilePage onBack={() => setShowProfile(false)} />
          ) : selectedModel === null ? (
            <LandingPage onSelectMode={handleSelectMode} />
          ) : selectedModel === "vehicle" ? (
            <VehicleProvider autoResetCalibration>
              <VehicleModelWithSwitcher
                setShowProfile={setShowProfile}
                onExit={handleExit}
              />
            </VehicleProvider>
          ) : selectedModel === "owner" ? (
            <VehicleProvider>
              <OwnerModelWithSwitcher
                setShowProfile={setShowProfile}
                onExit={handleExit}
              />
            </VehicleProvider>
          ) : (
            <FatigueProvider>
              <StandardModelWithSwitcher
                setShowProfile={setShowProfile}
                onExit={handleExit}
              />
            </FatigueProvider>
          )}
        </ModeProvider>
      </UserProvider>
    </ThemeProvider>
  );
};

export default App;
