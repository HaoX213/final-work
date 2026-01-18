import React, { useState, useCallback, useRef } from 'react';
import { Leva, useControls } from 'leva';
import { Canvas } from '@react-three/fiber';
import UnifiedWaveScene from './components/UnifiedWaveScene';
import CrossSectionGraph from './components/CrossSectionGraph';
import PhysicsExplainer from './components/PhysicsExplainer';

// Error Boundary for safety
class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  render() { 
      if (this.state.hasError) {
          return (
            <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', background: 'white', color: 'red', zIndex: 9999, padding: '20px' }}>
                <h1>CRITICAL ERROR</h1>
                <pre>{this.state.error?.toString()}</pre>
                <pre>{this.state.error?.stack}</pre>
            </div>
          );
      }
      return this.props.children; 
  }
}

export default function App() {
  const [viewMode, setViewMode] = useState('2D');
  const [activeParam, setActiveParam] = useState(null);
  
  // Slice Line State (World Z coordinate: -10 to 10)
  const [sliceY, setSliceY] = useState(0);

  // Leva Controls
  const physicsParams = useControls('物理参数控制', {
    separation: { 
        value: 4, min: 0, max: 10, label: '波源间距 (d)',
        onEditStart: () => setActiveParam('separation'),
        onEditEnd: () => setActiveParam(null)
    },
    frequency: { 
        value: 2, min: 1, max: 20, label: '频率 (f)',
        onEditStart: () => setActiveParam('frequency'),
        onEditEnd: () => setActiveParam(null)
    },
    phase: { 
        value: 0, min: 0, max: Math.PI * 2, label: '相位差 (φ)',
        onEditStart: () => setActiveParam('phase'),
        onEditEnd: () => setActiveParam(null)
    },
    gain: { 
        value: 0.5, min: 0.1, max: 2, label: '振幅增益 (A)',
        onEditStart: () => setActiveParam('gain'),
        onEditEnd: () => setActiveParam(null)
    },
    damping: { 
        value: 0.1, min: 0, max: 1, label: '阻尼系数',
        onEditStart: () => setActiveParam('damping'),
        onEditEnd: () => setActiveParam(null)
    },
    speed: { 
        value: 1.0, min: 0, max: 5, label: '时间速度',
        onEditStart: () => setActiveParam('speed'),
        onEditEnd: () => setActiveParam(null)
    }
  });

  return (
    <div className="w-full h-screen bg-black text-cyan-400 font-sans overflow-hidden flex flex-col items-stretch selection:bg-cyan-900 selection:text-white">

      {/* Leva Panel */}
      <div className="absolute top-16 right-4 z-50">
        <Leva 
            fill 
            flat 
            titleBar={{ drag: true, title: '物理参数控制' }} 
            theme={{
                colors: {
                    highlight1: '#00ffff',
                    highlight2: '#00aaaa',
                    highlight3: '#008888',
                    accent1: '#00ffff',
                    accent2: '#00aaaa',
                    accent3: '#008888',
                }
            }}
        />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 w-full relative h-full flex flex-col">
        
        {/* UPPER PART: CANVAS / 3D VIEW */}
        <div 
            className="relative w-full transition-[height] duration-700 ease-[cubic-bezier(0.25,0.1,0.25,1.0)]"
            style={{ height: viewMode === '2D' ? '60%' : '100%' }}
        >
            <ErrorBoundary>
                <Canvas shadows dpr={[1, 2]} camera={{ position: [0, 10, 10], fov: 45 }}>
                    <color attach="background" args={['#010204']} />
                    <fog attach="fog" args={['#010204', 10, 60]} />
                    <UnifiedWaveScene 
                        viewMode={viewMode} 
                        params={physicsParams} 
                        sliceY={sliceY} 
                        // onSliceUpdate={setSliceY}
                    />
                    
                    {/* Interaction Plane for Slice Line */}
                    {viewMode === '2D' && (
                        <mesh 
                            rotation={[-Math.PI / 2, 0, 0]} 
                            position={[0, 1, 0]}
                            visible={false} 
                            onPointerMove={(e) => {
                                const z = Math.max(-10, Math.min(10, e.point.z));
                                setSliceY(z);
                            }}
                        >
                            <planeGeometry args={[20, 20]} />
                        </mesh>
                    )}
                </Canvas>
            </ErrorBoundary>
            
            {/* View Mode Overlay Text */}
            <div className="absolute top-4 left-4 pointer-events-none z-20">
                <div className="border-l-4 border-cyan-500 pl-4 bg-black/60 pr-6 py-2 backdrop-blur-sm rounded-r-lg">
                    <h1 className="text-2xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                        波的干涉与叠加 V2.1
                    </h1>
                    <div className="text-sm font-semibold text-cyan-200 mt-1 flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${viewMode === '2D' ? 'bg-green-500' : 'bg-purple-500 animate-pulse'}`}></span>
                        模式: {viewMode === '2D' ? '2D 剖面分析 (ORTHO)' : '3D 交互视图 (ORBIT)'}
                    </div>
                </div>
            </div>

            {/* Explainer Panel */}
            <PhysicsExplainer activeParam={activeParam} />
        </div>

        {/* LOWER PART: CROSS SECTION GRAPH */}
        {/* Rendered always but height animated to 0 in 3D mode to preserve context/state */}
        <div 
            className="w-full bg-black border-t border-cyan-900 overflow-hidden transition-[height] duration-700 ease-[cubic-bezier(0.25,0.1,0.25,1.0)]"
            style={{ height: viewMode === '2D' ? '40%' : '0%' }}
        >
            <CrossSectionGraph sliceY={sliceY} params={physicsParams} />
        </div>
      </div>

      {/* BOTTOM BAR */}
      <div className="h-12 bg-[#050505] border-t border-cyan-900/50 flex items-center justify-between px-6 z-40 shrink-0 select-none">
         <div className="text-xs text-cyan-600/60 font-mono flex gap-4">
            <span>SIMULATION_ACTIVE</span>
            <span>R3F_RENDERER</span>
         </div>
         
         <div className="absolute left-1/2 -translate-x-1/2 -top-4">
            <button 
                onClick={() => setViewMode(v => v === '2D' ? '3D' : '2D')}
                className={`
                    px-8 py-2 rounded-full border border-cyan-500/50 text-sm font-bold tracking-widest transition-all duration-300 backdrop-blur-md shadow-[0_0_15px_rgba(0,255,255,0.1)]
                    hover:scale-105 hover:bg-cyan-500 hover:text-black active:scale-95
                    ${viewMode === '2D' 
                        ? 'bg-black/80 text-cyan-400' 
                        : 'bg-cyan-900/40 text-white border-purple-500 shadow-[0_0_20px_rgba(168,85,247,0.4)]'}
                `}
            >
                {viewMode === '2D' ? '进入 3D 视图' : '返回 2D 分析'}
            </button>
         </div>

         <div className="text-xs text-right text-cyan-700">
            <div>VERSION 2.1.0</div>
            <div>PHYSICS ENGINE ONLINE</div>
         </div>
      </div>

    </div>
  );
}
