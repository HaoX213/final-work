import { useCallback } from 'react';

/**
 * useWavePhysics Hook
 * Core physics logic for wave superposition.
 * Based on: y(r, t) = A * sin(k * r - w * t + phi)
 * 
 * @param {Object} params
 * @param {Array<{x: number, y: number}>} params.sources - Position of wave sources
 * @param {number} params.frequency - Spatial frequency (k)
 * @param {number} params.time - Current time (t)
 * @param {number} params.phaseOffset - Phase offset between sources
 * @param {number} params.damping - Distance attenuation coefficient (optional)
 * @returns {Function} getAmplitude(x, y) -> number
 */
export function useWavePhysics({ 
    sources = [], 
    frequency = 1, 
    time = 0, 
    phaseOffset = 0,
    damping = 0
}) {
    // A constant angular velocity for the wave animation (omega)
    const omega = 2.0; 
    const amplitude = 1.0;

    /**
     * Calculates amplitude at a specific point (x, y)
     * Returns the superposition of all waves.
     */
    const getAmplitude = useCallback((x, y) => {
        let totalVal = 0;

        for (let i = 0; i < sources.length; i++) {
            const { x: sx, y: sy } = sources[i];
            const dx = x - sx;
            const dy = y - sy;
            // distance r
            const r = Math.sqrt(dx * dx + dy * dy);

            // phase calculation:
            // k * r: Spatial component (k = frequency)
            // - omega * t: Temporal component
            // + phi: Phase offset. Source 0 gets 0, Source 1 gets phaseOffset, etc.
            const phi = i * phaseOffset; 
            
            // Damping: A * e^(-damping * r)
            // If damping is 0, factor is 1.
            const attenuation = Math.exp(-damping * r);

            // y = A sin(kr - wt + phi)
            totalVal += (amplitude * attenuation) * Math.sin((frequency * r) - (omega * time) + phi);
        }

        return totalVal;
    }, [sources, frequency, time, phaseOffset, omega, amplitude, damping]);

    return getAmplitude;
}
