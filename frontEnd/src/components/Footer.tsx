export default function Footer() {
    
  return (
    <footer className="bg-primary text-primary-foreground py-4 mt-8">
      <div className="container mx-auto px-4 text-center text-sm">
        © {new Date().getFullYear()} ConfidenTech — All rights reserved.
      </div>
    </footer>
  );
}
