import { User, Mail, Pencil } from "lucide-react";

const ProfileCard = ({ profile }) => {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-8 shadow-lg">
      <div className="flex flex-col items-center">
        {/* Avatar */}
        <div className="flex h-24 w-24 items-center justify-center rounded-full bg-indigo-600 text-white">
          <User size={42} />
        </div>

        {/* Name */}
        <h2 className="mt-5 text-2xl font-bold text-white">
          {profile.name || "Loading..."}
        </h2>

        {/* Email */}
        <div className="mt-2 flex items-center gap-2 text-sm text-zinc-400">
          <Mail size={16} />
          <span>{profile.email || "Loading..."}</span>
        </div>

        {/* Edit Button */}
        <button
          className="mt-6 flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700"
          type="button"
        >
          <Pencil size={16} />
          Edit Profile
        </button>
      </div>
    </div>
  );
};

export default ProfileCard;