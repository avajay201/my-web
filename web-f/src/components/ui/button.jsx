export function Button({ children, onClick, className = "", style = {}, disabled = false }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 rounded-lg transition-all duration-300 
        ${disabled ? "bg-gray-600" : ""} 
        ${className}`}
      style={style}
    >
      {children}
    </button>
  );
}
