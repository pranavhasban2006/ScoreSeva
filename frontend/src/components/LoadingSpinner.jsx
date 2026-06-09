export default function LoadingSpinner({ message = "Analysing..." }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4">
      <div className="relative w-14 h-14">
        <div className="absolute inset-0 rounded-full border-4
                        border-brand-orange-light" />
        <div className="absolute inset-0 rounded-full border-4
                        border-brand-orange border-t-transparent
                        animate-spin" />
      </div>
      <p className="text-sm font-medium text-gray-500">{message}</p>
    </div>
  );
}
