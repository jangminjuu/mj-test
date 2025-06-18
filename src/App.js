import React from 'react';

const HomePage = () => {
  return (
    <div style={{
      fontFamily: 'Nanum Gothic, sans-serif',
      textAlign: 'center',
      padding: '40px 20px',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: '#FFF0F5', // 연한 핑크 배경
      color: '#333'
    }}>
      <h1 style={{
        fontSize: '3.5em',
        color: '#FF69B4', // 핫핑크 제목
        marginBottom: '15px',
        textShadow: '1px 1px 2px rgba(0,0,0,0.1)'
      }}>
        장민주
      </h1>
      <p style={{
        fontSize: '1.2em',
        color: '#DA70D6', // 연보라색 본문
        marginBottom: '40px',
        maxWidth: '600px',
        lineHeight: '1.6'
      }}>
        안녕하세요! 섬세하고 꼼꼼한 QA 엔지니어 장민주입니다. <br/>
        저의 경험과 노력을 이곳에서 확인해 보세요 :)
      </p>
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: '20px',
        marginTop: '20px'
      }}>
        <LinkButton href="https://jangminju.notion.site/5e467245c3f14d67bdf9a4cd659e8f87">
          이력서
        </LinkButton>
        <LinkButton href="https://jangminju.notion.site/6fee4f285ff947b1bf22ae2f942ddc21">
          기술 스택
        </LinkButton>
        <LinkButton href="https://jangminju.notion.site/QA-_-1f52579c47f0464b91acf06b81621eec">
          QA 업무 시나리오
        </LinkButton>
         <LinkButton href="https://jangminju.notion.site/2de2f6eeb7c647508f0490d72452e470?v=958fbce6401f49ebaf7250e333517776">
          SKILL
        </LinkButton>
        <LinkButton href="https://minju-rani.tistory.com/">
          티스토리
        </LinkButton>
      </div>
    </div>
  );
};

// 링크 버튼 컴포넌트
const LinkButton = ({ href, children }) => {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        display: 'inline-block',
        padding: '12px 25px',
        backgroundColor: '#FFB6C1', // 연한 핑크 버튼
        color: 'white',
        textDecoration: 'none',
        borderRadius: '25px', // 둥근 버튼
        fontWeight: 'bold',
        fontSize: '1.1em',
        boxShadow: '0px 4px 6px rgba(0,0,0,0.1)', // 그림자 효과
        transition: 'all 0.3s ease',
        border: 'none',
        cursor: 'pointer'
      }}
      onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#FF69B4'} // 호버 시 핫핑크
      onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#FFB6C1'} // 원래 색상으로
    >
      {children}
    </a>
  );
};

export default HomePage;