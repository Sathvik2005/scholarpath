import { useEffect, useRef } from 'react';
import * as THREE from 'three';

// A literal 3D rendering of the six eligibility dimensions the matching
// engine scores. Each axis is one dimension; the shape's reach on each axis
// shows how close a sample student is to fully eligible (5 of 6 eligible,
// Documentation partial). Falls back via onUnsupported if WebGL is missing,
// doesn't animate under prefers-reduced-motion, and pauses off-screen.
const DIMENSIONS = [
  { label: 'Academic', value: 1.0, color: 0x2d8577 },
  { label: 'Financial', value: 1.0, color: 0x2d8577 },
  { label: 'Demographic', value: 1.0, color: 0x2d8577 },
  { label: 'Geographic', value: 1.0, color: 0x2d8577 },
  { label: 'Documentation', value: 0.55, color: 0xc98a2c },
  { label: 'Deadline', value: 1.0, color: 0x2d8577 },
];
const RADIUS = 1.35;

function axisPoint(i, r) {
  const angle = (Math.PI * 2 * i) / DIMENSIONS.length - Math.PI / 2;
  return new THREE.Vector3(Math.cos(angle) * r, 0, Math.sin(angle) * r);
}

export default function FitRadar3D({ onUnsupported }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    } catch {
      onUnsupported?.();
      return undefined;
    }

    const size = canvas.clientWidth || 300;
    renderer.setSize(size, size, false);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
    camera.position.set(0, 2.1, 4.4);
    camera.lookAt(0, 0.1, 0);
    scene.add(new THREE.AmbientLight(0xffffff, 0.75));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
    dirLight.position.set(2, 3, 2);
    scene.add(dirLight);

    const group = new THREE.Group();
    scene.add(group);

    // Radar spokes and two scale rings.
    const axisMat = new THREE.LineBasicMaterial({ color: 0xe4dfd2 });
    DIMENSIONS.forEach((_, i) => {
      const geo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), axisPoint(i, RADIUS)]);
      group.add(new THREE.Line(geo, axisMat));
    });
    [0.5, 1.0].forEach((frac) => {
      const pts = DIMENSIONS.map((_, i) => axisPoint(i, RADIUS * frac));
      group.add(new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts), axisMat));
    });

    // The fit shape: a filled polygon plus an edge outline.
    const shape = new THREE.Shape(
      DIMENSIONS.map((d, i) => {
        const p = axisPoint(i, RADIUS * d.value);
        return new THREE.Vector2(p.x, p.z);
      })
    );
    const shapeGeo = new THREE.ShapeGeometry(shape);
    shapeGeo.rotateX(-Math.PI / 2); // lay the XY shape flat onto the XZ ground plane

    const fitMesh = new THREE.Mesh(
      shapeGeo,
      new THREE.MeshStandardMaterial({
        color: 0x2d8577,
        transparent: true,
        opacity: 0.55,
        roughness: 0.5,
        metalness: 0.05,
        side: THREE.DoubleSide,
      })
    );
    fitMesh.position.y = 0.05;
    group.add(fitMesh);

    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(shapeGeo),
      new THREE.LineBasicMaterial({ color: 0x2d8577 })
    );
    edges.position.y = 0.052;
    group.add(edges);

    // Vertex markers, colored per dimension's verdict.
    DIMENSIONS.forEach((d, i) => {
      const p = axisPoint(i, RADIUS * d.value);
      const dot = new THREE.Mesh(
        new THREE.SphereGeometry(0.06, 16, 16),
        new THREE.MeshStandardMaterial({ color: d.color })
      );
      dot.position.set(p.x, 0.08, p.z);
      group.add(dot);
    });
    group.rotation.x = -0.25;

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let raf = null;
    const renderOnce = () => renderer.render(scene, camera);
    const loop = () => {
      group.rotation.y += 0.0035;
      renderOnce();
      raf = requestAnimationFrame(loop);
    };

    renderOnce();
    // Only animate while on-screen.
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !reduceMotion && !raf) raf = requestAnimationFrame(loop);
        if (!entry.isIntersecting && raf) {
          cancelAnimationFrame(raf);
          raf = null;
        }
      },
      { threshold: 0.05 }
    );
    observer.observe(canvas);

    return () => {
      observer.disconnect();
      if (raf) cancelAnimationFrame(raf);
      scene.traverse((obj) => {
        obj.geometry?.dispose();
        obj.material?.dispose();
      });
      renderer.dispose();
    };
  }, [onUnsupported]);

  return (
    <canvas ref={canvasRef} className="fit3d-canvas" width="300" height="300" style={{ width: 300, height: 300 }} />
  );
}
