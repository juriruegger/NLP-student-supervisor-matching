import Image from "next/image";

type ProfileImageProps = {
  src: string;
  name?: string;
};

export function ProfileImage({ src, name }: ProfileImageProps) {
  return (
    <Image
      src={src}
      alt={name ?? "Profile image"}
      width={80}
      height={80}
      className="rounded-full"
    />
  );
}
