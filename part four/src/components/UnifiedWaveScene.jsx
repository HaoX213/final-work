import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Environment, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';

// -----------------------------------------------------------------------------
// SHADERS
// -----------------------------------------------------------------------------

const vertexShader = `
  uniform float uTime;
  uniform float uFrequency;
  uniform float uPhase;
  uniform float uDamping;
  uniform float uAmplitude;
  uniform float uSpeed;
  uniform vec2 uSources[2]; 

  varying float vElevation;
  varying vec2 vUv;

  void main() {
    vUv = uv;
    vec4 modelPosition = modelMatrix * vec4(position, 1.0);
    
    float totalElevation = 0.0;
    
    for(int i = 0; i < 2; i++) {
        vec2 source = uSources[i];
        float dist = distance(modelPosition.xy, source);
        float attenuation = exp(-uDamping * dist);
        float phi = float(i) * uPhase;
        float wave = sin(uFrequency * dist - (2.0 * uTime * uSpeed) + phi);
        totalElevation += uAmplitude * attenuation * wave;
    }

    modelPosition.z += totalElevation;
    vElevation = totalElevation;

    vec4 viewPosition = viewMatrix * modelPosition;
    vec4 projectedPosition = projectionMatrix * viewPosition;
    gl_Position = projectedPosition;
  }
`;

const fragmentShader = `
  varying float vElevation;
  varying vec2 vUv;
  uniform float uMaxAmp;

  // Function to calculate normal from elevation derivatives
  // This creates a "faceted" or "sharp" look which is great for tech demos
  vec3 calcNormal() {
      // dFdx/dFY gives change in screen space
      // We want to visualize the slope
      return normalize(vec3(-dFdx(vElevation) * 10.0, -dFdy(vElevation) * 10.0, 1.0));
  }

  void main() {
    float intensity = vElevation / (uMaxAmp * 2.0);
    
    // Base Colors
    vec3 cyan = vec3(0.0, 1.0, 1.0);
    vec3 magenta = vec3(1.0, 0.0, 1.0);
    vec3 deepBlue = vec3(0.0, 0.1, 0.3);
    
    vec3 albedo = mix(deepBlue, cyan, clamp(intensity, 0.0, 1.0));
    if(intensity < 0.0) {
        albedo = mix(deepBlue, magenta, clamp(abs(intensity), 0.0, 1.0));
    }

    // Fake Lighting
    vec3 normal = calcNormal();
    vec3 lightDir = normalize(vec3(1.0, 1.0, 2.0));
    float light = max(0.0, dot(normal, lightDir));
    
    // Specular
    vec3 viewDir = normalize(vec3(0.0, 0.0, 10.0)); // Approximate view
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
    
    // Fresnel / Rim
    float viewScale = 1.0; 
    // Simplified rim
    
    vec3 finalColor = albedo * (0.4 + 0.6 * light) + vec3(spec * 0.5);

    // Alpha/Grid logic
    // Add simple grid lines based on UV
    float gridStr = 0.0;
    float gridScale = 40.0;
    if (fract(vUv.x * gridScale) < 0.05 || fract(vUv.y * gridScale) < 0.05) {
        finalColor += vec3(0.2);
    }
    
    gl_FragColor = vec4(finalColor, 0.9);
  }
`;

// -----------------------------------------------------------------------------
// COMPONENTS
// -----------------------------------------------------------------------------

function WaveMesh({ params, separation, viewMode }) {
    const meshRef = useRef();
    
    const uniforms = useMemo(() => ({
        uTime: { value: 0 },
        uFrequency: { value: params.frequency },
        uPhase: { value: params.phase },
        uDamping: { value: params.damping },
        uAmplitude: { value: params.gain },
        uSpeed: { value: params.speed },
        uSources: { value: [new THREE.Vector2(-separation/2, 0), new THREE.Vector2(separation/2, 0)] },
        uMaxAmp: { value: 1.0 }
    }), []);

    useFrame((state) => {
        if (meshRef.current) {
            const material = meshRef.current.material;
            // Prevent crash if uniforms aren't ready
            if(material.uniforms) {
                material.uniforms.uTime.value = state.clock.getElapsedTime();
                material.uniforms.uFrequency.value = params.frequency;
                material.uniforms.uPhase.value = params.phase;
                material.uniforms.uDamping.value = params.damping;
                material.uniforms.uAmplitude.value = params.gain;
                material.uniforms.uSpeed.value = params.speed;
                material.uniforms.uSources.value = [
                    new THREE.Vector2(-separation/2, 0), 
                    new THREE.Vector2(separation/2, 0)
                ];
                material.uniforms.uMaxAmp.value = params.gain;
            }
        }
    });

    return (
        <mesh ref={meshRef} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[30, 30, 300, 300]} />
            <shaderMaterial
                vertexShader={vertexShader}
                fragmentShader={fragmentShader}
                uniforms={uniforms}
                wireframe={false} 
                side={THREE.DoubleSide}
                transparent={true}
            />
        </mesh>
    );
}

function SliceLine({ visible, y, width = 20 }) {
    if (!visible) return null;
    return (
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.5, y]}>
            <planeGeometry args={[width, 0.1]} />
            <meshBasicMaterial color="#ffff00" opacity={0.8} transparent />
        </mesh>
    );
}

function CameraRig({ viewMode }) {
    const { camera } = useThree();
    const vec = new THREE.Vector3();
    
    useFrame((state) => {
        if (viewMode === '3D') {
             // In 3D mode, let OrbitControls handle it usually.
             // We only intervene if we want auto-rotate or initial transition.
             // For now, we DO NOTHING in 3D mode so user can rotate.
             return;
        }

        // 2D Mode: Lock to top down
        state.camera.position.lerp(vec.set(0, 35, 0), 0.05);
        state.camera.lookAt(0, 0, 0);
    });

    return null;
}

export default function UnifiedWaveScene({ viewMode, params, sliceY }) {
    return (
        <>
            <group>
                <WaveMesh params={params} separation={params.separation} viewMode={viewMode} />
                <SliceLine visible={viewMode === '2D'} y={sliceY} />
            </group>
            
            <CameraRig viewMode={viewMode} />
            
            {/* 3D Mode Improvements */}
            {viewMode === '3D' && (
                <>
                    <OrbitControls 
                        enablePan={false} 
                        minPolarAngle={0} 
                        maxPolarAngle={Math.PI / 2.2} // Restrict going below ground
                        minDistance={5}
                        maxDistance={50}
                        autoRotate={true}
                        autoRotateSpeed={0.5}
                    />
                    <ambientLight intensity={0.5} />
                    <pointLight position={[10, 10, 10]} intensity={1} />
                    <gridHelper args={[60, 60, 0x111111, 0x050505]} position={[0, -0.1, 0]} />
                </>
            )}
        </>
    );
}
