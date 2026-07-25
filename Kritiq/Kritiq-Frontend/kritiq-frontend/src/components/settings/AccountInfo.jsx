import { User, Mail, Fingerprint } from "lucide-react";

const AccountInfo = ({ profile }) => {
  return (
    <div className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-900 p-6 shadow-lg">
      <h2 className="mb-6 text-xl font-semibold text-white">
        Account Information
      </h2>

      <div className="space-y-5">
        {/* User ID */}
        <div className="flex items-start gap-4 rounded-xl bg-zinc-800/50 p-4">
          <Fingerprint className="mt-1 text-indigo-400" size={20} />
          <div>
            <p className="text-sm text-zinc-400">User ID</p>
            <p className="mt-1 break-all text-white">
              {profile.id || "Loading..."}
            </p>
          </div>
        </div>

        {/* Name */}
        <div className="flex items-start gap-4 rounded-xl bg-zinc-800/50 p-4">
          <User className="mt-1 text-indigo-400" size={20} />
          <div>
            <p className="text-sm text-zinc-400">Full Name</p>
            <p className="mt-1 text-white">
              {profile.name || "Loading..."}
            </p>
          </div>
        </div>

        {/* Email */}
        <div className="flex items-start gap-4 rounded-xl bg-zinc-800/50 p-4">
          <Mail className="mt-1 text-indigo-400" size={20} />
          <div>
            <p className="text-sm text-zinc-400">Email Address</p>
            <p className="mt-1 text-white">
              {profile.email || "Loading..."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountInfo;