export function Input({ type = "text", value, onChange, placeholder, className = "", disabled = false, onKeyDown }) {
  return (
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      className={`p-2 border rounded-lg w-full 
        ${disabled ? "bg-gray-700 cursor-progress text-gray-400" : "text-black"} 
        ${className}`}
        onKeyDown={onKeyDown}
    />
  );
}
