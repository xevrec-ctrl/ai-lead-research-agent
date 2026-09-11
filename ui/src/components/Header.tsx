interface HeaderProps {
  glassStyle: string;
}

const Header = ({ glassStyle }: HeaderProps) => {
  return (
    <div className="relative mb-16">
      <div className="text-center pt-4">
        <h1 className="text-3xl md:text-5xl font-medium text-[#1a202c] font-['DM_Sans'] tracking-normal leading-tight text-center mx-auto antialiased">
          客户线索研究与方案决策 Agent
        </h1>
        <p className="text-gray-600 text-lg font-['DM_Sans'] mt-4">
          企业调研、机会判断与可追溯方案生成
        </p>
      </div>
    </div>
  );
};

export default Header;
