import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  MdDashboard,
  MdPeople,
  MdPayment,
  MdSecurity,
  MdGroup,
} from 'react-icons/md';

const menuItems = [
  { path: '/dashboard', label: 'Dashboard', icon: MdDashboard },
  { path: '/users', label: 'Users', icon: MdPeople },
  { path: '/transactions', label: 'Transactions', icon: MdPayment },
  { path: '/roles', label: 'Roles', icon: MdSecurity },
  { path: '/groups', label: 'Groups', icon: MdGroup },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="bg-white dark:bg-gray-800 w-64 min-h-screen shadow-lg">
      <div className="p-4">
        <h1 className="text-2xl font-bold text-primary-600">Admin Panel</h1>
      </div>
      <nav className="mt-8">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.path;
            return (
              <li key={item.path}>
                <Link
                  href={item.path}
                  className={`flex items-center px-4 py-3 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 ${
                    isActive ? 'bg-primary-50 text-primary-600 dark:bg-primary-900 dark:text-primary-400' : ''
                  }`}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
} 