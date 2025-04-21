import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FaReact } from 'react-icons/fa'; // React logo icon
import { IoArrowBack } from 'react-icons/io5'; // Back arrow icon

export default function TopNav() {
  const router = useRouter();

  const handleGoBack = () => {
    router.back();
  };

  return (
    <nav className="bg-gray-900 text-white shadow-md sticky top-0 z-40">
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left Section: Logo & Back Button */}
          <div className="flex items-center space-x-4">
            <Link href="/dashboard" className="flex items-center space-x-2 flex-shrink-0">
              <FaReact className="h-8 w-8 text-cyan-400" />
              <span className="font-bold text-xl hidden md:block">Admin Panel</span>
            </Link>
            <button
              onClick={handleGoBack}
              title="Go Back"
              className="p-2 rounded-full hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-white"
            >
              <IoArrowBack className="h-5 w-5" />
              <span className="sr-only">Go Back</span>
            </button>
          </div>

          {/* Center Section: Navigation Links (Placeholder) */}
          <div className="hidden md:flex space-x-4">
            {/* Add main navigation links here if needed - distinct from sidebar */}
            {/* Example: */}
            {/* <Link href="/settings" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700">Settings</Link> */}
          </div>

          {/* Right Section: Can be used for user menu, notifications etc. - Handled by Header for now */}
          <div>
            {/* Content handled by the Header component below */}
          </div>
        </div>
      </div>
    </nav>
  );
} 