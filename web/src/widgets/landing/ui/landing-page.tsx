import Link from "next/link";
import { TopBar } from "@/widgets/top-bar";

/**
 * 랜딩 페이지 — design.html 기반 포팅 (ADR-0019).
 * hero / manifesto / 3 features / footer.
 */
export function LandingPage() {
  return (
    <main className="view">
      <TopBar active="landing" />

      {/* HERO */}
      <section className="paper relative overflow-hidden border-b border-border">
        <div className="mx-auto max-w-[1400px] px-6 pb-24 pt-24 md:px-10 md:pb-32 md:pt-36">
          <div className="grid items-start gap-16 lg:grid-cols-12">
            <div className="fade-up lg:col-span-7">
              <div className="mb-10 inline-flex items-center gap-2 rounded-full border border-border-strong bg-surface/50 py-1 pl-1.5 pr-3 text-[12px] text-text-muted">
                <span className="rounded bg-accent px-1.5 py-0.5 font-mono text-[10px] text-white">
                  NEW
                </span>
                대화형 디자인 스튜디오 v2 출시
              </div>

              <h1 className="font-serif text-[44px] leading-[1.1] tracking-tight text-text md:text-[68px]">
                기획을 <span className="text-accent">프롬프트</span>에,
                <br />
                구현은 <span className="text-accent">코드</span>로.
              </h1>

              <p className="mt-8 max-w-[580px] text-[17px] font-light leading-[1.6] text-text-soft md:text-[19px]">
                디자이너 없이도 완성도 높은 UI를 만들 수 있는 AI 디자인 스튜디오. 화면 구조,
                상태별 UI, 디자인 토큰, 복사 가능한 React 코드까지. 이제 대화로 다듬습니다.
              </p>

              <div className="mt-12 flex flex-wrap items-center gap-4">
                <Link
                  href="/studio"
                  className="inline-flex items-center gap-2 rounded-md bg-accent px-6 py-3.5 text-[15px] font-medium text-white transition hover:bg-accent-hover"
                >
                  스튜디오에서 시작하기
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.2"
                  >
                    <path d="M5 12h14M13 5l7 7-7 7" />
                  </svg>
                </Link>
                <a
                  href="#features"
                  className="inline-flex items-center gap-2 rounded-md border border-border-strong px-6 py-3.5 text-[15px] text-text transition hover:border-text-muted hover:bg-surface/50"
                >
                  핵심 기능 살펴보기
                </a>
              </div>

              <div className="mt-16 grid max-w-[480px] grid-cols-3 gap-8 border-t border-border pt-8">
                <Stat value="6+" label="상태 자동 생성" />
                <Stat value="0ms" label="수동 코딩" />
                <Stat value="MIT" label="코드 라이선스" />
              </div>
            </div>

            <HeroPreview />
          </div>
        </div>
      </section>

      {/* MANIFESTO */}
      <section className="border-b border-border">
        <div className="mx-auto max-w-[1000px] px-6 py-20 text-center md:px-10 md:py-28">
          <div className="fade-up mb-6 font-mono text-[11px] uppercase tracking-[0.2em] text-text-faint">
            WHY DEVCANVAS
          </div>
          <h2 className="fade-up delay-1 font-serif text-[28px] leading-[1.35] tracking-tight text-text-soft md:text-[40px]">
            &ldquo;예쁜 이미지&rdquo;가 아니라{" "}
            <span className="text-accent">&ldquo;당장 붙여 쓸 수 있는 결과물&rdquo;</span>을
            만듭니다.
            <br />한 화면이 아니라 전체 상태(Loading, Empty, Error)까지 함께.
          </h2>
        </div>
      </section>

      {/* FEATURE 1 */}
      <section id="features" className="border-b border-border bg-surface">
        <div className="mx-auto max-w-[1400px] px-6 py-24 md:px-10 md:py-32">
          <div className="grid items-center gap-12 lg:grid-cols-12">
            <div className="fade-up lg:col-span-5">
              <FeatureTag>01 — PROCESS</FeatureTag>
              <h2 className="mb-6 font-serif text-[36px] leading-[1.15] tracking-tight text-text md:text-[44px]">
                프롬프트 한 줄이
                <br />
                <span className="text-accent">전체 화면 구조</span>로.
              </h2>
              <p className="max-w-[480px] text-[16px] leading-[1.7] text-text-muted">
                화면 하나를 찍어주는 도구와 다릅니다. 비즈니스 맥락을 이해하고, 라우팅 계층을
                설계하며, 각 페이지가 담당할 역할을 정의합니다. 당연히 상태별 UI도 함께.
              </p>
              <div className="mt-8 space-y-3">
                <Checklist title="자연어 요구사항 분석" desc="복잡한 비즈니스 로직도 이해합니다." />
                <Checklist title="정보 아키텍처 설계" desc="URL 구조와 페이지 위계를 자동으로." />
                <Checklist title="대화로 반복 정제" desc="&ldquo;버튼 더 둥글게&rdquo;, &ldquo;모바일은 카드형으로&rdquo;." />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURE 2 */}
      <section className="border-b border-border bg-bg-soft paper">
        <div className="mx-auto max-w-[1400px] px-6 py-24 md:px-10 md:py-32">
          <div className="grid items-center gap-12 lg:grid-cols-12">
            <div className="fade-up order-1 lg:order-2 lg:col-span-6">
              <FeatureTag>02 — COMPLETENESS</FeatureTag>
              <h2 className="mb-6 font-serif text-[36px] leading-[1.15] tracking-tight text-text md:text-[44px]">
                한 화면이 아니라
                <br />
                <span className="text-accent">모든 상태</span>를 함께.
              </h2>
              <p className="max-w-[480px] text-[16px] leading-[1.7] text-text-muted">
                보통의 도구는 &lsquo;행복한 경로&rsquo;의 디자인 하나만 줍니다. DevCanvas는 로딩,
                빈 데이터, 에러, 권한 없음, 모바일까지 — 실 서비스에 필요한 모든 상태를 한 번에
                생성합니다. 디자이너가 가장 놓치기 쉬운 부분을 자동으로 채웁니다.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURE 3 */}
      <section className="border-b border-border bg-surface">
        <div className="mx-auto max-w-[1400px] px-6 py-24 md:px-10 md:py-32">
          <div className="grid items-center gap-12 lg:grid-cols-12">
            <div className="fade-up lg:col-span-5">
              <FeatureTag>03 — OUTPUT</FeatureTag>
              <h2 className="mb-6 font-serif text-[36px] leading-[1.15] tracking-tight text-text md:text-[44px]">
                복사하면
                <br />
                <span className="text-accent">그대로 동작하는</span> 코드.
              </h2>
              <p className="max-w-[480px] text-[16px] leading-[1.7] text-text-muted">
                Tailwind CSS와 shadcn/ui 기반의 표준 코드를 생성합니다. 디자인 토큰은 CSS 변수로
                관리되고, 컴포넌트는 프로젝트에 바로 붙여넣으면 동작합니다. 별도의 수동 작업이
                필요 없습니다.
              </p>
              <div className="mt-8 space-y-4">
                <OutputLine>
                  <code className="rounded bg-bg-soft px-1.5 py-0.5 font-mono">npm run dev</code>{" "}
                  바로 실행 가능
                </OutputLine>
                <OutputLine>Tailwind + shadcn/ui 표준 호환</OutputLine>
                <OutputLine>Next.js App Router 완벽 대응</OutputLine>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-border bg-bg">
        <div className="mx-auto flex max-w-[1400px] flex-col items-center justify-between gap-4 px-6 py-8 text-[12px] text-text-muted md:flex-row md:px-10">
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-sm bg-accent" />
            <span className="font-serif text-text">DevCanvas</span>
          </div>
          <div className="font-mono">기획을 코드로 · MIT</div>
        </div>
      </footer>
    </main>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <div className="font-serif text-[28px] text-text">{value}</div>
      <div className="mt-1 font-mono text-[11px] uppercase tracking-wider text-text-muted">
        {label}
      </div>
    </div>
  );
}

function FeatureTag({ children }: { children: React.ReactNode }) {
  return (
    <div className="mb-4 font-mono text-[11px] uppercase tracking-[0.2em] text-accent">
      {children}
    </div>
  );
}

function Checklist({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="flex items-start gap-3">
      <div className="mt-0.5 flex h-5 w-5 items-center justify-center rounded-full border border-success/30 bg-success-soft">
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#5C8A4A" strokeWidth="3">
          <path d="M20 6L9 17l-5-5" />
        </svg>
      </div>
      <div>
        <div className="text-[14px] font-medium text-text">{title}</div>
        <div className="text-[12px] text-text-muted">{desc}</div>
      </div>
    </div>
  );
}

function OutputLine({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-3 text-[14px] text-text">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1F1E1D" strokeWidth="2">
        <path d="M16 18l6-6-6-6M8 6l-6 6 6 6" />
      </svg>
      <span>{children}</span>
    </div>
  );
}

/** 히어로 우측 미리보기 카드 묶음 (대시보드 + 채팅 버블 + 토큰). */
function HeroPreview() {
  return (
    <div className="fade-up delay-2 relative hidden h-[480px] lg:col-span-5 lg:block">
      <div className="paper-dense absolute left-1/2 top-1/2 h-[110%] w-[110%] -translate-x-1/2 -translate-y-1/2 rounded-full opacity-60" />

      {/* 대시보드 카드 */}
      <div className="absolute right-0 top-8 w-[360px] rotate-1 overflow-hidden rounded-lg border border-border bg-surface shadow-[0_2px_4px_rgba(31,30,29,0.04),0_12px_32px_-12px_rgba(31,30,29,0.1)] transition-transform duration-500 hover:rotate-0">
        <div className="flex h-8 items-center gap-1.5 border-b border-border bg-bg-soft/50 px-3">
          <div className="h-2 w-2 rounded-full bg-border-strong" />
          <div className="h-2 w-2 rounded-full bg-border-strong" />
          <div className="h-2 w-2 rounded-full bg-border-strong" />
          <div className="ml-3 font-mono text-[10px] text-text-faint">app/page.tsx</div>
        </div>
        <div className="p-4">
          <div className="mb-3 flex items-center gap-2">
            <div className="flex h-5 w-5 items-center justify-center rounded-md border border-accent/20 bg-accent-soft">
              <div className="h-2 w-2 rounded-sm bg-accent" />
            </div>
            <div className="font-serif text-[14px] text-text">고객 대시보드</div>
            <span className="ml-auto rounded bg-success-soft px-1.5 py-0.5 font-mono text-[9px] text-success">
              default
            </span>
          </div>
          <div className="mb-3 grid grid-cols-3 gap-2">
            <DashStat k="MRR" v="₩12.4M" />
            <DashStat k="ACTIVE" v="1,102" />
            <DashStat k="CHURN" v="1.4%" />
          </div>
          <div className="space-y-1.5 rounded border border-border bg-bg-soft p-2">
            <DashRow name="김지호" v="₩29,000" />
            <DashRow name="박서아" v="₩59,000" />
            <DashRow name="이도윤" v="₩0" />
          </div>
        </div>
      </div>

      {/* 채팅 버블 */}
      <div className="absolute left-0 top-0 z-10 w-[280px] -rotate-3 rounded-lg rounded-tl-sm border border-border bg-surface p-3 shadow-sm transition-transform duration-500 hover:rotate-0">
        <div className="mb-1.5 flex items-center gap-1.5">
          <div className="flex h-4 w-4 items-center justify-center rounded-sm bg-text">
            <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3">
              <path d="M12 5v14M5 12h14" />
            </svg>
          </div>
          <span className="font-mono text-[10px] text-text-muted">user</span>
        </div>
        <p className="text-[11px] leading-relaxed text-text">
          정기결제 SaaS 관리자 페이지 만들어줘. 결제 상태 필터와 상세 보기 포함.
        </p>
      </div>

      {/* 토큰 카드 */}
      <div className="absolute bottom-12 left-4 w-[180px] rotate-3 rounded-md border border-border bg-surface p-3 shadow-sm transition-transform duration-500 hover:rotate-0">
        <div className="mb-2 border-b border-border pb-1.5 font-mono text-[9px] uppercase tracking-wider text-text-faint">
          design tokens
        </div>
        <div className="flex flex-wrap gap-1">
          <Token color="#FAF9F5" border />
          <Token color="#1F1E1D" />
          <Token color="#C96442" />
          <Token color="#5C8A4A" />
          <Token color="#B5524A" />
          <Token color="#F0EEE6" border />
        </div>
        <div className="mt-2 font-mono text-[9px] text-text-muted">6 colors extracted</div>
      </div>
    </div>
  );
}

function DashStat({ k, v }: { k: string; v: string }) {
  return (
    <div className="rounded border border-border bg-bg-soft p-2">
      <div className="font-mono text-[9px] text-text-muted">{k}</div>
      <div className="mt-0.5 font-mono text-[12px] text-text">{v}</div>
    </div>
  );
}

function DashRow({ name, v }: { name: string; v: string }) {
  return (
    <div className="flex items-center justify-between text-[10px]">
      <div className="flex items-center gap-1.5">
        <div className="h-4 w-4 rounded-full bg-accent/20" />
        <span className="text-text">{name}</span>
      </div>
      <span className="font-mono text-text-muted">{v}</span>
    </div>
  );
}

function Token({ color, border }: { color: string; border?: boolean }) {
  return (
    <div
      className="h-4 w-4 rounded-sm"
      style={{ background: color, border: border ? "1px solid #E5E2D8" : undefined }}
    />
  );
}
