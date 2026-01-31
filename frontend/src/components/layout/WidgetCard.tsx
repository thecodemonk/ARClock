import { ReactNode } from "react";

interface Props {
  title: string;
  rightHeader?: ReactNode;
  children: ReactNode;
}

export default function WidgetCard({ title, rightHeader, children }: Props) {
  return (
    <div className="widget-card">
      <div className="widget-card-header">
        <span>{title}</span>
        {rightHeader}
      </div>
      <div className="widget-card-body">{children}</div>
    </div>
  );
}
