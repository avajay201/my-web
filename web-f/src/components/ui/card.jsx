export function Card({ children, className = "", onClick, style = {} }) {
  return (
    <div
      onClick={onClick}
      className={`p-4 border rounded-lg shadow-md bg-gray-800 text-white cursor-pointer ${className}`}
      style={style}
    >
      {children}
    </div>
  );
}

export function CardContent({ children, style = {} }) {
  return <div className="text-center" style={style}>{children}</div>;
}
