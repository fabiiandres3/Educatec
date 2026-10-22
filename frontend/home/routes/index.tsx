import { createFileRoute } from "@tanstack/react-router";
import { motion, useScroll, useTransform, useSpring, AnimatePresence, useMotionValue, type MotionValue } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import {
  GraduationCap, ArrowRight, Shapes, BookOpen, Rocket, CalendarDays, Clock, FlaskConical,
  Users, ClipboardCheck, Target, Megaphone, Eye, Menu, X, BarChart3, CalendarClock, NotebookPen, Sparkles,
} from "lucide-react";

const HERO_IMG = "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1600&q=80";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Educatec · Plataforma educativa" },
      { name: "description", content: "Educatec reúne a estudiantes, docentes y familias: seguimiento académico, tareas, calificaciones, horarios y eventos del colegio." },
      { property: "og:title", content: "Educatec · Plataforma educativa" },
      { property: "og:description", content: "La tecnología al servicio de la educación." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { property: "og:image", content: HERO_IMG },
      { name: "twitter:image", content: HERO_IMG },
    ],
    links: [
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700;800&family=Figtree:wght@400;500;600&display=swap" },
    ],
  }),
  component: Index,
});

const ease = [0.22, 1, 0.36, 1] as const;

const niveles = [
  { key: "Preescolar", n: "01", href: "/prescolar", img: "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=1400", icon: Shapes, edad: "2 – 5 años",
    text: "Un entorno seguro y divertido donde los niños desarrollan creatividad, autonomía y habilidades sociales mediante el aprendizaje basado en el juego.",
    items: ["Estimulación temprana", "Desarrollo psicomotor", "Inglés inicial", "Expresión artística"] },
  { key: "Primaria", n: "02", href: "/primaria", img: "https://images.unsplash.com/photo-1588072432836-e10032774350?w=1400", icon: BookOpen, edad: "6 – 11 años",
    text: "Fomentamos el pensamiento crítico, la curiosidad y el trabajo colaborativo mediante experiencias de aprendizaje innovadoras.",
    items: ["Ciencias y matemáticas", "Tecnología educativa", "Inglés intensivo", "Proyectos STEAM"] },
  { key: "Secundaria", n: "03", href: "/secundaria", img: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1400", icon: Rocket, edad: "12 – 17 años",
    text: "Preparamos a nuestros alumnos para afrontar retos académicos y profesionales mediante liderazgo, innovación y orientación vocacional.",
    items: ["Programación y tecnología", "Liderazgo estudiantil", "Orientación vocacional", "Preparación universitaria"] },
];

const tipos: Record<string, { label: string; icon: typeof FlaskConical }> = {
  academico: { label: "Académico", icon: FlaskConical }, reunion: { label: "Reunión", icon: Users },
  evaluacion: { label: "Evaluación", icon: ClipboardCheck }, actividad: { label: "Actividad", icon: Target }, aviso: { label: "Aviso", icon: Megaphone },
};

// Eventos de ejemplo (en el sitio real vienen del sistema del colegio)
const eventos = [
  { id: 1, tipo: "academico", titulo: "Feria de Ciencias", descripcion: "Los estudiantes presentan sus proyectos de investigación ante la comunidad educativa.", dia: "14", mes: "NOV", hora: "08:00 – 12:00", img: "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=900" },
  { id: 2, tipo: "reunion", titulo: "Reunión de padres", descripcion: "Entrega de informes del periodo y diálogo con los directores de grupo.", dia: "20", mes: "NOV", hora: "07:00 – 09:00", img: "https://images.unsplash.com/photo-1577962917302-cd874c4e31d2?w=900" },
  { id: 3, tipo: "actividad", titulo: "Olimpiadas deportivas", descripcion: "Una jornada de competencia sana, trabajo en equipo y espíritu escolar.", dia: "28", mes: "NOV", hora: "08:00 – 15:00", img: "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=900" },
  { id: 4, tipo: "evaluacion", titulo: "Simulacro Saber 11", descripcion: "Prueba de preparación para los estudiantes de grado once.", dia: "03", mes: "DIC", hora: "07:00 – 13:00", img: "https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?w=900" },
];

/* ---------------- NAV ---------------- */
function Nav() {
  const [open, setOpen] = useState(false);
  const { scrollYProgress } = useScroll();
  const bar = useSpring(scrollYProgress, { stiffness: 120, damping: 30 });
  const links: [string, string][] = [["#niveles", "Niveles"], ["#plataforma", "Plataforma"], ["#eventos", "Eventos"], ["#nosotros", "Nosotros"]];
  return (
    <>
      <motion.div style={{ scaleX: bar }} className="fixed inset-x-0 top-0 z-[60] h-0.5 origin-left bg-gradient-primary" />
      <motion.header initial={{ y: -80, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.8, ease }}
        className="fixed inset-x-0 top-4 z-50 mx-auto w-[min(94%,960px)]">
        <div className="glass flex items-center justify-between rounded-full px-4 py-2.5 sm:px-6">
          <a href="#" className="flex items-center gap-2 font-display font-bold">
            <span className="grid h-8 w-8 place-items-center rounded-full bg-gradient-primary"><GraduationCap className="h-4 w-4" /></span>
            Educatec
          </a>
          <nav className="hidden items-center gap-7 text-sm text-muted-foreground md:flex">
            {links.map(([h, l]) => <a key={h} href={h} className="transition hover:text-foreground">{l}</a>)}
          </nav>
          <a href="/login" className="hidden rounded-full bg-foreground px-4 py-1.5 text-sm font-semibold text-background transition hover:scale-105 md:inline-block">Iniciar sesión</a>
          <button onClick={() => setOpen(!open)} className="md:hidden" aria-label="Menú">{open ? <X /> : <Menu />}</button>
        </div>
        <AnimatePresence>
          {open && (
            <motion.nav initial={{ opacity: 0, y: -10, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -10 }}
              className="glass mt-2 flex flex-col gap-4 rounded-3xl p-6 md:hidden">
              {links.map(([h, l]) => <a key={h} href={h} onClick={() => setOpen(false)} className="text-lg">{l}</a>)}
              <a href="/login" className="rounded-full bg-foreground py-3 text-center font-semibold text-background">Iniciar sesión</a>
            </motion.nav>
          )}
        </AnimatePresence>
      </motion.header>
    </>
  );
}

/* ---------------- HERO (Apple-style zoom) ---------------- */
function Hero() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end end"] });
  const scale = useTransform(scrollYProgress, [0, 0.6], [0.55, 1]);
  const radius = useTransform(scrollYProgress, [0, 0.6], [48, 0]);
  const textY = useTransform(scrollYProgress, [0, 0.4], [0, -200]);
  const textOp = useTransform(scrollYProgress, [0, 0.3], [1, 0]);
  const overlayOp = useTransform(scrollYProgress, [0.55, 0.85], [0, 1]);

  const mx = useMotionValue(0), my = useMotionValue(0);
  const rx = useSpring(useTransform(my, [-0.5, 0.5], [6, -6]), { stiffness: 80, damping: 20 });
  const ry = useSpring(useTransform(mx, [-0.5, 0.5], [-6, 6]), { stiffness: 80, damping: 20 });

  return (
    <section ref={ref} className="relative h-[220vh]"
      onMouseMove={(e) => { mx.set(e.clientX / window.innerWidth - 0.5); my.set(e.clientY / window.innerHeight - 0.5); }}>
      <div className="sticky top-0 flex h-screen flex-col items-center justify-center overflow-hidden">
        <div className="grid-bg absolute inset-0" />
        <div className="absolute left-1/2 top-1/3 h-[50vw] w-[50vw] -translate-x-1/2 animate-spin-slow rounded-full bg-[conic-gradient(from_0deg,var(--primary),transparent,var(--primary-glow),transparent,var(--primary))] opacity-25 blur-3xl" />

        <motion.div style={{ y: textY, opacity: textOp }} className="relative z-10 px-5 text-center">
          <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 0.8, ease }}
            className="mb-5 inline-flex items-center gap-2 rounded-full border border-border px-4 py-1.5 text-xs tracking-[0.3em] text-muted-foreground">
            <Sparkles className="h-3.5 w-3.5 text-highlight" /> PLATAFORMA EDUCATIVA
          </motion.p>
          <h1 className="text-5xl font-extrabold leading-[0.95] sm:text-7xl lg:text-[8.5rem]">
            {["La tecnología", "al servicio de la"].map((l, i) => (
              <span key={l} className="block overflow-hidden">
                <motion.span className="block" initial={{ y: "110%" }} animate={{ y: 0 }} transition={{ delay: 0.4 + i * 0.15, duration: 1, ease }}>{l}</motion.span>
              </span>
            ))}
            <span className="block overflow-hidden">
              <motion.span className="text-gradient block" initial={{ y: "110%" }} animate={{ y: 0 }} transition={{ delay: 0.7, duration: 1, ease }}>educación.</motion.span>
            </span>
          </h1>
        </motion.div>

        <motion.div style={{ scale, borderRadius: radius, rotateX: rx, rotateY: ry, transformPerspective: 1200 }}
          className="absolute inset-0 overflow-hidden shadow-glow">
          <motion.img initial={{ opacity: 0 }} animate={{ opacity: 0.35 }} transition={{ delay: 1, duration: 1.2 }}
            src={HERO_IMG} alt="Estudiantes trabajando en equipo" className="h-full w-full object-cover" />
          <motion.div style={{ opacity: overlayOp }} className="absolute inset-0 flex flex-col items-center justify-center bg-background/60 px-5 text-center backdrop-blur-sm">
            <p className="max-w-3xl text-2xl font-light leading-snug sm:text-4xl">
              Educatec reúne a <b className="font-bold text-primary-glow">estudiantes</b>, <b className="font-bold text-primary-glow">docentes</b> y <b className="font-bold text-primary-glow">familias</b> en un mismo entorno.
            </p>
            <div className="mt-10 flex flex-wrap justify-center gap-4">
              <a href="#niveles" className="group inline-flex items-center gap-2 rounded-full bg-gradient-primary px-7 py-3.5 font-semibold text-primary-foreground shadow-glow transition hover:scale-105">
                Explorar niveles <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
              </a>
              <a href="/login" className="glass rounded-full px-7 py-3.5 font-semibold transition hover:bg-foreground hover:text-background">Iniciar sesión</a>
            </div>
          </motion.div>
        </motion.div>

        <motion.div style={{ opacity: textOp }} className="absolute bottom-8 z-10 flex flex-col items-center gap-2 text-xs text-muted-foreground">
          Desliza
          <motion.span animate={{ y: [0, 8, 0] }} transition={{ repeat: Infinity, duration: 1.6 }} className="h-8 w-[1px] bg-gradient-to-b from-foreground to-transparent" />
        </motion.div>
      </div>
    </section>
  );
}

/* ---------------- WORD REVEAL ---------------- */
function Word({ w, range, p }: { w: string; range: [number, number]; p: MotionValue<number> }) {
  const o = useTransform(p, range, [0.12, 1]);
  return <motion.span style={{ opacity: o }} className="mr-[0.25em] inline-block">{w}</motion.span>;
}
function Manifesto() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start 0.8", "end 0.4"] });
  const text = "Seguimiento académico, tareas, calificaciones, horarios y eventos del colegio. Todo en un solo lugar.";
  const words = text.split(" ");
  return (
    <section ref={ref} className="mx-auto max-w-5xl px-5 py-40">
      <p className="font-display text-3xl font-bold leading-tight sm:text-6xl">
        {words.map((w, i) => <Word key={i} w={w} p={scrollYProgress} range={[i / words.length, (i + 1) / words.length]} />)}
      </p>
    </section>
  );
}

/* ---------------- NIVELES: horizontal pinned scroll ---------------- */
function Niveles() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref });
  const x = useTransform(scrollYProgress, [0, 1], ["0%", "-66.666%"]);
  const progress = useTransform(scrollYProgress, [0, 1], ["0%", "100%"]);
  return (
    <section id="niveles" ref={ref} className="relative h-[300vh]">
      <div className="sticky top-0 flex h-screen flex-col overflow-hidden">
        <div className="mx-auto w-full max-w-7xl px-5 pt-28">
          <p className="text-sm tracking-[0.3em] text-primary-glow">FORMACIÓN INTEGRAL</p>
          <div className="mt-3 flex flex-col justify-between gap-4 md:flex-row md:items-end">
            <h2 className="max-w-2xl text-4xl font-extrabold sm:text-6xl">Acompañamos cada etapa del crecimiento.</h2>
            <p className="max-w-sm text-muted-foreground">Desde los primeros años hasta la preparación para la educación superior, cada nivel cuenta con su propio panel dentro de la plataforma.</p>
          </div>
          <div className="mt-6 h-px w-full bg-border"><motion.div style={{ width: progress }} className="h-full bg-gradient-primary" /></div>
        </div>
        <motion.div style={{ x }} className="flex w-[300%] flex-1">
          {niveles.map((n) => (
            <div key={n.key} className="flex w-1/3 items-center px-5 py-8">
              <div className="mx-auto grid h-full max-h-[60vh] w-full max-w-7xl gap-6 md:grid-cols-2">
                <div className="group relative overflow-hidden rounded-[2rem]">
                  <img src={n.img} alt={`Aula de ${n.key}`} loading="lazy" className="h-full w-full object-cover transition duration-1000 group-hover:scale-110" />
                  <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent" />
                  <span className="absolute bottom-4 left-6 font-display text-[7rem] font-extrabold leading-none text-foreground/15 sm:text-[10rem]">{n.n}</span>
                </div>
                <div className="glass flex flex-col justify-center rounded-[2rem] p-7 sm:p-10">
                  <div className="flex items-center gap-3">
                    <span className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-primary"><n.icon className="h-6 w-6" /></span>
                    <span className="text-sm text-muted-foreground">{n.edad}</span>
                  </div>
                  <h3 className="mt-5 text-4xl font-extrabold sm:text-5xl">{n.key}</h3>
                  <p className="mt-4 text-muted-foreground">{n.text}</p>
                  <div className="mt-6 flex flex-wrap gap-2">
                    {n.items.map((it) => <span key={it} className="rounded-full border border-border px-3 py-1.5 text-xs">{it}</span>)}
                  </div>
                  <a href={n.href} className="group mt-8 inline-flex items-center gap-2 font-semibold text-primary-glow">
                    Conocer más <ArrowRight className="h-4 w-4 transition group-hover:translate-x-2" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

/* ---------------- PLATAFORMA: bento ---------------- */
function Tilt({ children, className }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: 50, y: 50 });
  return (
    <motion.div ref={ref} initial={{ opacity: 0, y: 60 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-80px" }} transition={{ duration: 0.9, ease }}
      onMouseMove={(e) => { const r = ref.current!.getBoundingClientRect(); setPos({ x: ((e.clientX - r.left) / r.width) * 100, y: ((e.clientY - r.top) / r.height) * 100 }); }}
      style={{ backgroundImage: `radial-gradient(500px circle at ${pos.x}% ${pos.y}%, color-mix(in oklab, var(--primary) 22%, transparent), transparent 45%)` }}
      className={`glass relative overflow-hidden rounded-[2rem] p-8 ${className ?? ""}`}>
      {children}
    </motion.div>
  );
}
function Plataforma() {
  return (
    <section id="plataforma" className="mx-auto max-w-7xl px-5 py-32">
      <motion.h2 initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.9, ease }}
        className="mx-auto mb-16 max-w-3xl text-center text-4xl font-extrabold sm:text-6xl">
        Una plataforma. <span className="text-gradient">Toda la comunidad.</span>
      </motion.h2>
      <div className="grid auto-rows-[minmax(220px,auto)] gap-5 md:grid-cols-3">
        <Tilt className="md:col-span-2 md:row-span-2">
          <BarChart3 className="h-10 w-10 text-primary-glow" />
          <h3 className="mt-6 text-3xl font-bold sm:text-4xl">Seguimiento académico</h3>
          <p className="mt-3 max-w-md text-muted-foreground">Estudiantes, docentes y familias ven el progreso en tiempo real.</p>
          <div className="mt-10 flex h-40 items-end gap-3">
            {[40, 65, 50, 80, 70, 95, 85].map((h, i) => (
              <motion.div key={i} initial={{ height: 0 }} whileInView={{ height: `${h}%` }} viewport={{ once: true }} transition={{ delay: 0.3 + i * 0.08, duration: 0.8, ease }}
                className="flex-1 rounded-t-xl bg-gradient-primary" />
            ))}
          </div>
        </Tilt>
        <Tilt><NotebookPen className="h-8 w-8 text-highlight" /><h3 className="mt-5 text-2xl font-bold">Tareas</h3><p className="mt-2 text-sm text-muted-foreground">Entregas y pendientes organizados.</p></Tilt>
        <Tilt>
          <ClipboardCheck className="h-8 w-8 text-primary-glow" /><h3 className="mt-5 text-2xl font-bold">Calificaciones</h3>
          <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="text-gradient mt-3 font-display text-5xl font-extrabold">4.8</motion.p>
        </Tilt>
        <Tilt className="md:col-span-3">
          <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
            <div><CalendarClock className="h-8 w-8 text-highlight" /><h3 className="mt-5 text-2xl font-bold">Horarios y eventos del colegio</h3></div>
            <div className="flex gap-2">
              {["Lun", "Mar", "Mié", "Jue", "Vie"].map((d, i) => (
                <motion.span key={d} whileHover={{ y: -6 }} className={`grid h-16 w-12 place-items-center rounded-2xl border border-border text-sm sm:w-16 ${i === 2 ? "bg-gradient-primary" : ""}`}>{d}</motion.span>
              ))}
            </div>
          </div>
        </Tilt>
      </div>
    </section>
  );
}

/* ---------------- EVENTOS: stacked list w/ hover preview ---------------- */
function Eventos() {
  const [hover, setHover] = useState<number | null>(null);
  const [mouse, setMouse] = useState({ x: 0, y: 0 });
  return (
    <section id="eventos" className="relative mx-auto max-w-7xl px-5 py-32" onMouseMove={(e) => setMouse({ x: e.clientX, y: e.clientY })}>
      <div className="mb-14 flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-sm tracking-[0.3em] text-primary-glow">ACTIVIDADES</p>
          <h2 className="mt-3 text-4xl font-extrabold sm:text-6xl">Eventos del colegio.</h2>
        </div>
        <p className="max-w-sm text-muted-foreground">Actividades que fortalecen el espíritu de comunidad, la competencia sana y el desarrollo integral.</p>
      </div>
      {eventos.length ? (
        <div className="border-t border-border">
          {eventos.map((e, i) => {
            const t = tipos[e.tipo] ?? { label: "General", icon: CalendarDays };
            return (
              <motion.a key={e.id} href={`/eventos/${e.id}`} onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)}
                initial={{ opacity: 0, x: -40 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1, duration: 0.7, ease }}
                className="group grid grid-cols-[auto_1fr_auto] items-center gap-5 border-b border-border py-7 transition-colors hover:bg-card/50 sm:gap-10 sm:px-4">
                <div className="text-center font-display">
                  <p className="text-4xl font-extrabold transition group-hover:text-primary-glow sm:text-5xl">{e.dia}</p>
                  <p className="text-xs tracking-widest text-muted-foreground">{e.mes}</p>
                </div>
                <div>
                  <span className="inline-flex items-center gap-1.5 text-xs text-highlight"><t.icon className="h-3.5 w-3.5" />{t.label}</span>
                  <h3 className="mt-1 text-xl font-bold transition group-hover:translate-x-2 sm:text-3xl">{e.titulo}</h3>
                  <p className="mt-1 hidden text-sm text-muted-foreground sm:block">{e.descripcion}</p>
                  <p className="mt-2 flex items-center gap-1.5 text-xs text-muted-foreground"><Clock className="h-3.5 w-3.5" />{e.hora}</p>
                </div>
                <span className="grid h-12 w-12 place-items-center rounded-full border border-border transition group-hover:-rotate-45 group-hover:bg-foreground group-hover:text-background">
                  <ArrowRight className="h-5 w-5" />
                </span>
              </motion.a>
            );
          })}
        </div>
      ) : (
        <div className="glass rounded-[2rem] p-12 text-center">
          <CalendarDays className="mx-auto h-12 w-12 text-muted-foreground" />
          <h3 className="mt-4 text-xl font-bold">No hay eventos disponibles</h3>
          <p className="text-muted-foreground">Próximamente publicaremos nuevas actividades.</p>
        </div>
      )}
      <AnimatePresence>
        {hover !== null && (
          <motion.img key={hover} src={eventos[hover]?.img} alt="" initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.8 }}
            style={{ left: mouse.x + 24, top: mouse.y - 100 }}
            className="pointer-events-none fixed z-40 hidden h-48 w-72 rounded-2xl object-cover shadow-glow lg:block" />
        )}
      </AnimatePresence>
    </section>
  );
}

/* ---------------- NOSOTROS ---------------- */
function Nosotros() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const y1 = useTransform(scrollYProgress, [0, 1], [100, -100]);
  const y2 = useTransform(scrollYProgress, [0, 1], [-60, 60]);
  const galeria = [
    { img: "https://images.unsplash.com/photo-1562774053-701939374585?w=600", alt: "Laboratorio de ciencias", tag: "Ciencias", y: y1 },
    { img: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600", alt: "Alumnos con portátiles", tag: "Tecnología", y: y2 },
    { img: "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=600", alt: "Trabajo en equipo en la biblioteca", tag: "Biblioteca", y: y1 },
    { img: "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=600", alt: "Alumnos en el campus", tag: "Comunidad", y: y2 },
  ];
  const mv = [
    { icon: Target, t: "Misión", d: "Brindar una educación integral de alta calidad, desarrollando en los alumnos competencias académicas, tecnológicas y humanas. Buscamos formar jóvenes conscientes de su entorno, capaces de ingresar con éxito a la educación superior y liderar proyectos de transformación social." },
    { icon: Eye, t: "Visión", d: "Consolidarnos para el año 2030 como una institución líder en innovación pedagógica y tecnológica. Seremos reconocidos por el alto desempeño de nuestros egresados, su pensamiento crítico y su capacidad de adaptación a un mundo en constante evolución." },
  ];
  return (
    <section id="nosotros" ref={ref} className="overflow-hidden py-32">
      <div className="mx-auto max-w-5xl px-5 text-center">
        <p className="text-sm tracking-[0.3em] text-primary-glow">SOBRE NOSOTROS</p>
        <motion.h2 initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.9, ease }}
          className="mt-4 text-4xl font-extrabold sm:text-7xl">Una institución enfocada en el <span className="text-gradient">futuro</span> y la excelencia.</motion.h2>
        <p className="mx-auto mt-8 max-w-3xl text-lg text-muted-foreground">
          Nuestra propuesta educativa se centra en dotar a los jóvenes de herramientas críticas, científicas y tecnológicas necesarias para afrontar los retos universitarios y del entorno global. Fomentamos la autonomía, el liderazgo y el desarrollo del pensamiento complejo en un ambiente de alta exigencia académica.
        </p>
      </div>
      <div className="mx-auto mt-20 grid max-w-7xl grid-cols-2 gap-4 px-5 md:grid-cols-4">
        {galeria.map((g) => (
          <motion.div key={g.tag} style={{ y: g.y }} className="group relative overflow-hidden rounded-[1.75rem]">
            <img src={g.img} alt={g.alt} loading="lazy" className="aspect-[3/4] w-full object-cover grayscale transition duration-700 group-hover:scale-110 group-hover:grayscale-0" />
            <span className="glass absolute bottom-3 left-3 rounded-full px-3 py-1 text-xs">{g.tag}</span>
          </motion.div>
        ))}
      </div>
      <div className="mx-auto mt-24 grid max-w-7xl gap-5 px-5 md:grid-cols-2">
        {mv.map((m, i) => (
          <Tilt key={m.t}>
            <div className="flex items-center gap-3"><span className="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-primary"><m.icon /></span><span className="font-display text-sm text-muted-foreground">0{i + 1}</span></div>
            <h3 className="mt-6 text-3xl font-bold">{m.t}</h3>
            <p className="mt-3 text-muted-foreground">{m.d}</p>
          </Tilt>
        ))}
      </div>
    </section>
  );
}

/* ---------------- CTA + FOOTER ---------------- */
function Cta() {
  const items = ["Preescolar", "Primaria", "Secundaria", "Tareas", "Calificaciones", "Horarios", "Eventos"];
  return (
    <section className="relative overflow-hidden pb-10 pt-20">
      <div className="flex w-max animate-marquee gap-10 whitespace-nowrap font-display text-6xl font-extrabold text-foreground/10 sm:text-8xl">
        {[...items, ...items].map((t, i) => <span key={i}>{t} ✦</span>)}
      </div>
      <motion.div initial={{ opacity: 0, scale: 0.9 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }} transition={{ duration: 1, ease }}
        className="mx-auto mt-16 max-w-3xl px-5 text-center">
        <h2 className="text-4xl font-extrabold sm:text-6xl">El futuro de tu colegio empieza aquí.</h2>
        <a href="/login" className="group mt-10 inline-flex items-center gap-2 rounded-full bg-gradient-primary px-9 py-4 text-lg font-semibold text-primary-foreground shadow-glow transition hover:scale-105">
          Iniciar sesión <ArrowRight className="h-5 w-5 transition group-hover:translate-x-1" />
        </a>
      </motion.div>
      <footer className="mx-auto mt-28 flex max-w-7xl flex-col items-center justify-between gap-3 border-t border-border px-5 pt-8 text-sm text-muted-foreground sm:flex-row">
        <span className="flex items-center gap-2"><GraduationCap className="h-4 w-4" /> Educatec · Plataforma educativa</span>
        <span>La tecnología al servicio de la educación</span>
      </footer>
    </section>
  );
}

function Index() {
  const [ready, setReady] = useState(false);
  useEffect(() => setReady(true), []);
  return (
    <main className={`overflow-x-clip transition-opacity duration-700 ${ready ? "opacity-100" : "opacity-0"}`}>
      <Nav />
      <Hero />
      <Manifesto />
      <Niveles />
      <Plataforma />
      <Eventos />
      <Nosotros />
      <Cta />
    </main>
  );
}
