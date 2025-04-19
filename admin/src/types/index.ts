// User types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
}

export interface UserProfile {
  id: number;
  user: User;
  balance: number;
  qr_code_url: string | null;
  created_at: string;
  updated_at: string;
}

// Transaction types
export interface Transaction {
  id: number;
  sender: User;
  receiver: User;
  amount: number;
  transaction_type: 'PAYMENT' | 'TOP_UP' | 'REFUND';
  status: 'PENDING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  description: string;
  created_at: string;
  updated_at: string;
}

// Vendor types
export interface Vendor {
  id: number;
  user: User;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface VendorTransaction {
  id: number;
  vendor: Vendor;
  transaction: Transaction;
  created_at: string;
}

// Group types
export interface Group {
  id: number;
  name: string;
  description: string;
  users: User[];
  permissions: Permission[];
  created_at: string;
  updated_at: string;
}

// Permission types
export interface Permission {
  id: number;
  name: string;
  codename: string;
  description: string;
  created_at: string;
  updated_at: string;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Dashboard types
export interface DashboardStats {
  total_users: number;
  total_vendors: number;
  total_transactions: number;
  total_amount: number;
  transactions_by_type: Record<string, number>;
  transactions_by_status: Record<string, number>;
  recent_transactions: Transaction[];
}

// Form types
export interface LoginForm {
  username: string;
  password: string;
}

export interface UserForm {
  username: string;
  email: string;
  password?: string;
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
  is_staff?: boolean;
}

export interface UserProfileForm {
  balance?: number;
}

export interface TransactionForm {
  receiver_id: number;
  amount: number;
  description?: string;
}

export interface VendorForm {
  name: string;
  description?: string;
}

export interface GroupForm {
  name: string;
  description?: string;
  users?: number[];
  permissions?: number[];
}

export interface PermissionForm {
  name: string;
  codename: string;
  description?: string;
} 