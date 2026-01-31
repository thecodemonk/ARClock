interface Props {
  time: string;
  date: string;
  label: string;
}

export default function ClockDisplay({ time, date, label }: Props) {
  return (
    <div className="clock-display">
      <div className="clock-time">{time}</div>
      <div className="clock-label">{label}</div>
      <div className="clock-date">{date}</div>
    </div>
  );
}
