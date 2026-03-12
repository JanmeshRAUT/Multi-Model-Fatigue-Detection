import React, { useRef, useMemo, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { RoundedBox, Environment, OrbitControls } from "@react-three/drei";
import "./Css/EyeModel.css";

function EyeVisualization({ perclos = 0, ear = 0.3, status = "Open" }) {
  const groupRef = useRef();
  const leftEyelidTopRef = useRef();
  const leftEyelidBotRef = useRef();
  const rightEyelidTopRef = useRef();
  const rightEyelidBotRef = useRef();
  
  const [blinkPhase, setBlinkPhase] = useState(0);
  
  // Normalize PERCLOS (0-100% to 0-1)
  const normalizedPerclos = Math.max(0, Math.min(1, perclos / 100));
  const normalizedEAR = Math.max(0, Math.min(1, ear / 0.4));
  
  // Eye opening based on EAR
  const eyeOpenAmount = Math.max(0.2, normalizedEAR);
  
  // Dynamic eye color based on PERCLOS
  const eyeColor = useMemo(() => {
    if (status === "Closed" || normalizedPerclos > 0.95) return "#000000";
    if (normalizedPerclos > 0.65) return "#FF0000"; // Red - critical
    if (normalizedPerclos > 0.45) return "#FF4500"; // Orange-red - high
    if (normalizedPerclos > 0.25) return "#FFB700"; // Orange - medium
    if (normalizedPerclos > 0.1) return "#90EE90"; // Light green - low
    return "#00FF00"; // Bright green - alert
  }, [status, normalizedPerclos]);
  
  // Iris glow intensity
  const glowIntensity = Math.max(0.5, 1 - normalizedPerclos * 0.6);

  // Blinking animation
  useEffect(() => {
    let blinkTimer;
    const scheduleBlinkCycle = () => {
      const blinkInterval = Math.random() * 2000 + 3000;
      blinkTimer = setTimeout(() => {
        setBlinkPhase(0);
        let progress = 0;
        const blinkTick = setInterval(() => {
          progress += 0.06;
          setBlinkPhase(progress);
          
          if (progress >= 1) {
            clearInterval(blinkTick);
            scheduleBlinkCycle();
          }
        }, 16);
      }, blinkInterval);
    };
    
    scheduleBlinkCycle();
    return () => clearTimeout(blinkTimer);
  }, []);

  // Eyelid animation and head tilt
  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    
    // Head tilt
    if (groupRef.current) {
      groupRef.current.rotation.z = Math.sin(time * 0.3) * 0.02;
    }
    
    // Blink animation
    const blinkEffect = Math.sin(blinkPhase * Math.PI);
    const fatigueClosing = Math.max(0, Math.min(1, normalizedPerclos * 0.6));
    const combinedClosing = blinkEffect * 0.5 + fatigueClosing * 0.4;
    
    // Update eyelids
    [leftEyelidTopRef, rightEyelidTopRef].forEach(ref => {
      if (ref.current) {
        ref.current.position.y = 0.25 - combinedClosing * 0.35;
        ref.current.scale.y = Math.max(0.1, 1 - combinedClosing * 0.7);
      }
    });
    
    [leftEyelidBotRef, rightEyelidBotRef].forEach(ref => {
      if (ref.current) {
        ref.current.position.y = -0.25 + combinedClosing * 0.35;
        ref.current.scale.y = Math.max(0.1, 1 - combinedClosing * 0.7);
      }
    });
  });

  return (
    <group ref={groupRef}>
      {/* Main Head - Clean Rounded Box */}
      <RoundedBox args={[2.0, 1.8, 1.4]} radius={0.25} smoothness={4}>
        <meshStandardMaterial 
          color="#f5f5f5" 
          roughness={0.2} 
          metalness={0.05}
          envMapIntensity={1}
        />
      </RoundedBox>

      {/* LEFT EYE */}
      <group position={[-0.5, 0.15, 0.75]}>
        <mesh>
          <circleGeometry args={[0.3, 32]} />
          <meshStandardMaterial color="#1a1a1a" roughness={0.3} />
        </mesh>
        
        <mesh position={[0, 0, 0.05]} scale={[eyeOpenAmount * 0.85, eyeOpenAmount, 1]}>
          <circleGeometry args={[0.15, 32]} />
          <meshStandardMaterial 
            color={eyeColor}
            emissive={eyeColor}
            emissiveIntensity={glowIntensity}
            roughness={0.2}
            metalness={0.3}
          />
        </mesh>
        
        <mesh position={[0, 0, 0.06]}>
          <circleGeometry args={[0.08, 32]} />
          <meshStandardMaterial color="#000000" roughness={0.1} metalness={0.9} />
        </mesh>

        <mesh position={[0.05, 0.05, 0.07]}>
          <circleGeometry args={[0.03, 16]} />
          <meshStandardMaterial 
            color="#ffffff" 
            emissive="#ffffff" 
            emissiveIntensity={2}
          />
        </mesh>

        <mesh ref={leftEyelidTopRef} position={[0, 0.28, 0.08]}>
          <boxGeometry args={[0.5, 0.1, 0.15]} />
          <meshStandardMaterial color="#e0e0e0" roughness={0.4} metalness={0.05} />
        </mesh>
        
        <mesh ref={leftEyelidBotRef} position={[0, -0.28, 0.08]}>
          <boxGeometry args={[0.5, 0.1, 0.15]} />
          <meshStandardMaterial color="#e0e0e0" roughness={0.4} metalness={0.05} />
        </mesh>
      </group>

      {/* RIGHT EYE */}
      <group position={[0.5, 0.15, 0.75]}>
        <mesh>
          <circleGeometry args={[0.3, 32]} />
          <meshStandardMaterial color="#1a1a1a" roughness={0.3} />
        </mesh>
        
        <mesh position={[0, 0, 0.05]} scale={[eyeOpenAmount * 0.85, eyeOpenAmount, 1]}>
          <circleGeometry args={[0.15, 32]} />
          <meshStandardMaterial 
            color={eyeColor}
            emissive={eyeColor}
            emissiveIntensity={glowIntensity}
            roughness={0.2}
            metalness={0.3}
          />
        </mesh>
        
        <mesh position={[0, 0, 0.06]}>
          <circleGeometry args={[0.08, 32]} />
          <meshStandardMaterial color="#000000" roughness={0.1} metalness={0.9} />
        </mesh>

        <mesh position={[-0.05, 0.05, 0.07]}>
          <circleGeometry args={[0.03, 16]} />
          <meshStandardMaterial 
            color="#ffffff" 
            emissive="#ffffff" 
            emissiveIntensity={2}
          />
        </mesh>

        <mesh ref={rightEyelidTopRef} position={[0, 0.28, 0.08]}>
          <boxGeometry args={[0.5, 0.1, 0.15]} />
          <meshStandardMaterial color="#e0e0e0" roughness={0.4} metalness={0.05} />
        </mesh>
        
        <mesh ref={rightEyelidBotRef} position={[0, -0.28, 0.08]}>
          <boxGeometry args={[0.5, 0.1, 0.15]} />
          <meshStandardMaterial color="#e0e0e0" roughness={0.4} metalness={0.05} />
        </mesh>
      </group>
    </group>
  );
}

export default function EyeModel3D({ perclos = 0, ear = 0.3, status = "Open" }) {
  // Validate inputs
  const safePerclos = typeof perclos === "number" ? perclos : 0;
  const safeEar = typeof ear === "number" ? ear : 0.3;
  const safeStatus = typeof status === "string" ? status : "Open";
  
  return (
    <div className="eye-model-container">
      <Canvas 
        camera={{ position: [0, 0, 2.5], fov: 50 }} 
        style={{ width: '100%', height: '100%' }}
      >
        <ambientLight intensity={0.8} />
        <directionalLight position={[5, 10, 7]} intensity={1.2} />
        <pointLight position={[0, 0, 2]} intensity={0.7} color="#4ade80" />
        
        <EyeVisualization perclos={safePerclos} ear={safeEar} status={safeStatus} />
        
        <Environment preset="studio" intensity={1.3} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate={false} />
      </Canvas>
    </div>
  );
}
