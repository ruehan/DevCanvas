import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import "./globals.css";

const jbmono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jbmono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "DevCanvas — 기획을 코드로 만들어주는 AI 디자인 스튜디오",
  description:
    "디자이너 없이도 완성도 높은 UI를 만들 수 있는 AI 디자인 스튜디오. 화면 구조, 상태별 UI, 디자인 토큰, 복사 가능한 React 코드까지.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" className={jbmono.variable}>
      <head>
        {/* GmarketSans (한국어 본문/디스플레이) — webfontworld CDN (ADR-0019) */}
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/webfontworld/gmarketsans/GmarketSans.css"
        />
      </head>
      <body className="font-sans">{children}</body>
    </html>
  );
}
