import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

const baseProps = {
  width: 20,
  height: 20,
  viewBox: "0 0 24 24",
  fill: "none"
} as const;

export const DashboardIcon = (props: IconProps) => (
  <svg {...baseProps} {...props}>
    <rect x="3" y="3" width="7.5" height="7.5" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
    <rect x="13.5" y="3" width="7.5" height="5.5" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
    <rect x="3" y="13.5" width="5.5" height="7.5" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
    <rect x="11.5" y="11.5" width="9.5" height="9.5" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
  </svg>
);

export const HammerIcon = (props: IconProps) => (
  <svg {...baseProps} {...props}>
    <path
      d="M14.5 6.5L18 10l-8.5 8.5a2.5 2.5 0 0 1-3.5 0 2.5 2.5 0 0 1 0-3.5L14.5 6.5Z"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M14.5 6.5L17 4l3 3-2.5 2.5"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M17 4L15 2"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
  </svg>
);

export const TeamAnalysisIcon = (props: IconProps) => (
  <svg {...baseProps} {...props}>
    <path
      d="M4 19h16"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
    <path
      d="M6 16l3-4 3 3 4-6 2 3"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <circle cx="9" cy="12" r="1.2" fill="currentColor" />
    <circle cx="12" cy="15" r="1.2" fill="currentColor" />
    <circle cx="16" cy="9" r="1.2" fill="currentColor" />
    <circle cx="18" cy="12" r="1.2" fill="currentColor" />
  </svg>
);

export const BinocularsIcon = (props: IconProps) => (
  <svg {...baseProps} {...props}>
    <circle cx="7" cy="14" r="4" stroke="currentColor" strokeWidth="1.5" />
    <circle cx="17" cy="14" r="4" stroke="currentColor" strokeWidth="1.5" />
    <path
      d="M7 10V7a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v3"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
    <path
      d="M11 14h2"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
  </svg>
);

export const MLBTeamsIcon = (props: IconProps) => (
  <svg {...baseProps} {...props}>
    <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.5" />
    <path
      d="M6 9c1.5 1 3.5 1.5 6 1.5 2.5 0 4.5-.5 6-1.5"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
    <path
      d="M6 15c1.5-1 3.5-1.5 6-1.5 2.5 0 4.5.5 6 1.5"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
    <path
      d="M12 3.5c.8 1.3 1.2 2.8 1.2 4.5s-.4 3.2-1.2 4.5c-.8-1.3-1.2-2.8-1.2-4.5s.4-3.2 1.2-4.5Z"
      fill="currentColor"
    />
    <path
      d="M12 11.5c.8 1.3 1.2 2.8 1.2 4.5s-.4 3.2-1.2 4.5c-.8-1.3-1.2-2.8-1.2-4.5s.4-3.2 1.2-4.5Z"
      fill="currentColor"
    />
  </svg>
);

export const navIcons = {
  dashboard: DashboardIcon,
  hammer: HammerIcon,
  teamAnalysis: TeamAnalysisIcon,
  binoculars: BinocularsIcon,
  mlbTeams: MLBTeamsIcon
} as const;

export type NavIconKey = keyof typeof navIcons;

