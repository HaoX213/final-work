
// Pure Physics Math Function
export function calculateAmplitude(x, y, t, sources, params) {
    const { frequency, phaseOffset, damping, amplitude = 1.0, omega = 2.0 } = params;
    
    let totalVal = 0;
    
    // Individual Wave Components
    const waves = sources.map((source, i) => {
        const dx = x - source.x;
        const dy = y - source.y;
        const r = Math.sqrt(dx * dx + dy * dy);
        const phi = i * phaseOffset;
        const attenuation = Math.exp(-damping * r);
        const val = (amplitude * attenuation) * Math.sin((frequency * r) - (omega * t) + phi);
        return val;
    });

    // Sum
    totalVal = waves.reduce((a, b) => a + b, 0);

    return { total: totalVal, components: waves };
}
