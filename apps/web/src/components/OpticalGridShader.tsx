import { useEffect, useRef } from "react";

/**
 * WebGL2 / GLSL precision-optics measurement grid & reticle shader background.
 * - Renders a drifting optical bench coordinate grid with gentle cursor parallax.
 * - Automatically pauses rendering when `document.hidden` is true.
 * - Immediately exits when `prefers-reduced-motion: reduce` is enabled.
 * - Capped at 1x devicePixelRatio so GPU cost stays minimal on laptops.
 */
export function OpticalGridShader() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (mediaQuery.matches) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const gl = canvas.getContext("webgl2", {
      alpha: true,
      antialias: false,
      powerPreference: "low-power",
    });
    if (!gl) return;

    const vsSource = `#version 300 es
      in vec2 a_pos;
      out vec2 v_uv;
      void main() {
        v_uv = a_pos * 0.5 + 0.5;
        gl_Position = vec4(a_pos, 0.0, 1.0);
      }
    `;

    const fsSource = `#version 300 es
      precision mediump float;
      in vec2 v_uv;
      uniform vec2 u_res;
      uniform float u_time;
      uniform vec2 u_mouse;
      out vec4 outColor;

      void main() {
        vec2 aspect = vec2(u_res.x / max(u_res.y, 1.0), 1.0);
        vec2 uv = (v_uv - 0.5) * aspect;
        vec2 m = (u_mouse - 0.5) * aspect;

        // Subtle drifting optical grid
        vec2 gridUv = uv * 14.0 + vec2(u_time * 0.06, u_time * 0.03) + m * 0.25;
        vec2 cell = abs(fract(gridUv - 0.5) - 0.5) / fwidth(gridUv);
        float line = min(cell.x, cell.y);
        float gridAlpha = 1.0 - min(line, 1.0);

        // Reticle focus ring around cursor
        float d = length(uv - m);
        float ring = smoothstep(0.22, 0.215, d) * smoothstep(0.205, 0.21, d);

        vec3 amber = vec3(1.0, 0.698, 0.122);
        vec3 baseLine = vec3(0.22, 0.24, 0.26);
        vec3 col = mix(baseLine, amber, ring * 0.85);
        float alpha = clamp(gridAlpha * 0.11 + ring * 0.22, 0.0, 0.26);
        outColor = vec4(col, alpha);
      }
    `;

    const compile = (type: number, src: string) => {
      const sh = gl.createShader(type);
      if (!sh) return null;
      gl.shaderSource(sh, src);
      gl.compileShader(sh);
      if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
        gl.deleteShader(sh);
        return null;
      }
      return sh;
    };

    const vs = compile(gl.VERTEX_SHADER, vsSource);
    const fs = compile(gl.FRAGMENT_SHADER, fsSource);
    if (!vs || !fs) return;

    const prog = gl.createProgram();
    if (!prog) return;
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(
      gl.ARRAY_BUFFER,
      new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
      gl.STATIC_DRAW,
    );

    const posLoc = gl.getAttribLocation(prog, "a_pos");
    const resLoc = gl.getUniformLocation(prog, "u_res");
    const timeLoc = gl.getUniformLocation(prog, "u_time");
    const mouseLoc = gl.getUniformLocation(prog, "u_mouse");

    let mouseX = 0.5;
    let mouseY = 0.5;
    const onMove = (e: PointerEvent) => {
      mouseX = e.clientX / Math.max(window.innerWidth, 1);
      mouseY = 1.0 - e.clientY / Math.max(window.innerHeight, 1);
    };
    window.addEventListener("pointermove", onMove, { passive: true });

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      gl.viewport(0, 0, canvas.width, canvas.height);
    };
    resize();
    window.addEventListener("resize", resize);

    let rafId = 0;
    const tStart = performance.now();

    const render = (now: number) => {
      if (!document.hidden) {
        gl.clearColor(0, 0, 0, 0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.useProgram(prog);
        gl.enableVertexAttribArray(posLoc);
        gl.bindBuffer(gl.ARRAY_BUFFER, buf);
        gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);
        gl.uniform2f(resLoc, canvas.width, canvas.height);
        gl.uniform1f(timeLoc, (now - tStart) * 0.001);
        gl.uniform2f(mouseLoc, mouseX, mouseY);
        gl.drawArrays(gl.TRIANGLES, 0, 6);
      }
      rafId = requestAnimationFrame(render);
    };
    rafId = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 opacity-80"
    />
  );
}
