import React, { useMemo } from 'react';

const DICTIONARY = {
  default: {
    title: "波的干涉与叠加原理",
    desc: "当两列波在同一介质中传播时，它们会在交汇处叠加。如果波峰遇到波峰，振幅增强（建设性干涉）；如果波峰遇到波谷，振幅抵消（破坏性干涉）。请尝试调整参数，观察干涉图样的变化。"
  },
  separation: {
    title: "波源间距 (d) 对干涉的影响",
    desc: "根据双缝干涉公式 Δx = Lλ/d，波源间距 d 与干涉条纹间距成反比。减小波源间距，条纹变得更宽、更稀疏；增大间距，条纹变得更加密集。这演示了波程差 Δr 随角度变化的敏感度。"
  },
  frequency: {
    title: "频率 (f)与波长 (λ)",
    desc: "频率决定了波的颜色（光波）或音调（声波）。根据 v = fλ，在波速恒定时，频率越高，波长越短。波长越短，衍射效应越不明显，干涉条纹会变得更加细密精细。"
  },
  phase: {
    title: "相位差 (φ) 的作用",
    desc: "相位差决定了两列波起步的相对时间。改变相位差会使整个干涉图样发生平移。当相位差为 π (180度) 时，原本的极大值点会变为极小值点，亮纹变暗纹。"
  },
  gain: {
    title: "振幅叠加原理 (A)",
    desc: "根据线性叠加原理 y = y1 + y2，合成波的振幅取决于两列波的叠加。最大振幅可达 2A（相长干涉），最小振幅为 0（相消干涉）。此滑块控制单个波源的能量。"
  },
  damping: {
    title: "介质阻尼与衰减",
    desc: "在真实物理环境中，波的能量会随距离传播而损耗（如水波摩擦、声波吸收）。衰减模型通常为 A(r) = A0 * e^(-αr)。高阻尼会导致波传播不远，干涉现象只能在波源附近观察到。"
  },
  speed: {
    title: "时域仿真控制",
    desc: "控制波动方程 y(r,t) = A sin(kr - ωt) 中的 t 变量变化率。减慢速度可以更清晰地观察波前的传播过程和每一个瞬时的叠加状态。"
  }
};

export default function PhysicsExplainer({ activeParam }) {
  const content = DICTIONARY[activeParam] || DICTIONARY.default;

  return (
    <div className="absolute bottom-20 left-4 w-96 p-6 bg-black/90 border-l-4 border-cyan-500 backdrop-blur-md shadow-[0_0_20px_rgba(0,100,100,0.3)] pointer-events-none transition-all duration-300 z-30">
      <h3 className="text-cyan-400 font-bold text-lg mb-3 flex items-center gap-2">
        <svg className="w-5 h-5 animate-spin-slow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        {content.title}
      </h3>
      <p className="text-gray-200 text-sm leading-7 font-sans text-justify">
        {content.desc}
      </p>
    </div>
  );
}
