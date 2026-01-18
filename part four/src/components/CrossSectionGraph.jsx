import React, { useEffect, useRef, useMemo } from 'react';
import { calculateAmplitude } from '../utils/physics';

export default function CrossSectionGraph({ sliceY, params }) {
    const canvasRef = useRef(null);
    const timeRef = useRef(0);

    const { separation, frequency, phase, gain, damping, speed } = params;

    // Derived sources for calculation
    const sources = useMemo(() => {
        const half = separation / 2;
        return [{ x: -half, y: 0 }, { x: half, y: 0 }];
    }, [separation]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        
        let animationId;
        
        const render = () => {
             // Sync time roughly with R3F (or just run own clock)
             // We increment time manually
             timeRef.current += 0.01 * speed;
             const t = timeRef.current;

             // Setup Canvas
             const width = canvas.width = canvas.parentElement.clientWidth;
             const height = canvas.height = canvas.parentElement.clientHeight;
             const halfH = height / 2;

             ctx.clearRect(0, 0, width, height);
             
             // Draw Axis
             ctx.strokeStyle = '#333';
             ctx.beginPath();
             ctx.moveTo(0, halfH);
             ctx.lineTo(width, halfH);
             ctx.stroke();

             // Physics Constants
             // World X range: -10 to 10 (Matches Mesh Size 20x20)
             const xMin = -10; 
             const xMax = 10;
             const xScale = width / (xMax - xMin);
             // Amplitude Scale: 1 unit = 50px? 
             const yScale = 50; 

             ctx.lineWidth = 2;

             // Arrays to hold points
             const pathTotal = new Path2D();
             const pathSource1 = new Path2D();
             const pathSource2 = new Path2D();
             
             let first = true;

             // Resolution of graph
             const steps = 200;
             
             for (let i = 0; i <= steps; i++) {
                 // Map step to World X
                 const xWorld = xMin + (i / steps) * (xMax - xMin);
                 // Canvas X
                 const xCanvas = i * (width / steps);
                 
                 // Calculate Physics
                 const result = calculateAmplitude(xWorld, sliceY, t, sources, {
                     frequency, phaseOffset: phase, damping, amplitude: gain
                 });
                 
                 // Map Amplitude to Canvas Y
                 // Invert Y because Canvas Y+ is down
                 const yTotal = halfH - (result.total * yScale);
                 const yS1 = halfH - (result.components[0] * yScale);
                 const yS2 = halfH - (result.components[1] * yScale);

                 if (first) {
                     pathTotal.moveTo(xCanvas, yTotal);
                     pathSource1.moveTo(xCanvas, yS1);
                     pathSource2.moveTo(xCanvas, yS2);
                     first = false;
                 } else {
                     pathTotal.lineTo(xCanvas, yTotal);
                     pathSource1.lineTo(xCanvas, yS1);
                     pathSource2.lineTo(xCanvas, yS2);
                 }
             }

             // Render Lines
             
             // Source 1: Blue Thin
             ctx.strokeStyle = 'rgba(0, 200, 255, 0.4)';
             ctx.lineWidth = 1;
             ctx.stroke(pathSource1);
             
             // Source 2: Green Thin
             ctx.strokeStyle = 'rgba(0, 255, 100, 0.4)';
             ctx.stroke(pathSource2);
             
             // Total: White Thick
             ctx.strokeStyle = '#ffffff';
             ctx.lineWidth = 3;
             ctx.shadowBlur = 5;
             ctx.shadowColor = 'white';
             ctx.stroke(pathTotal);
             ctx.shadowBlur = 0;

             animationId = requestAnimationFrame(render);
        };

        render();
        return () => cancelAnimationFrame(animationId);
    }, [sliceY, sources, frequency, phase, gain, damping, speed]); 

    return (
        <div className="w-full h-full relative bg-gray-900/80 border-t border-gray-700">
            <canvas ref={canvasRef} className="block w-full h-full" />
            <div className="absolute top-2 left-2 text-xs font-mono text-white opacity-70">
                CROSS-SECTION ANALYSIS (Y = {sliceY.toFixed(2)})
            </div>
            <div className="absolute bottom-2 right-4 text-xs font-mono flex gap-4">
                <span className="text-cyan-400">--- Source 1</span>
                <span className="text-green-400">--- Source 2</span>
                <span className="text-white font-bold">--- Composite</span>
            </div>
        </div>
    );
}
