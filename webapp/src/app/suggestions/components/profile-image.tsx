import Image from "next/image";

type ProfileImageProps = {
  src: string;
  name?: string;
};
/*
 * ProfileImage component displays a supervisor's profile image.
 */
export function ProfileImage({ src, name }: ProfileImageProps) {
  return (
    <div className="relative w-20 h-20 flex-shrink-0">
      <Image
        src={src}
        alt={name ?? "Profile image"}
        fill={true}
        className="rounded-full object-cover"
      />
    </div>
  );
}
