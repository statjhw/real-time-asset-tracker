import logging
import os
import sys
from datetime import datetime
from typing import Optional


class Logger:
    """
    프로젝트 전용 로거 클래스
    다양한 로그 레벨과 포맷팅을 지원합니다.
    """
    
    def __init__(self, name: str, log_level: str = "INFO", log_file: Optional[str] = None):
        """
        로거 초기화
        
        Args:
            name: 로거 이름
            log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: 로그 파일 경로 (None이면 콘솔만 출력)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 이미 핸들러가 설정되어 있다면 중복 방지
        if self.logger.handlers:
            return
            
        # 로그 포맷 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 파일 핸들러 추가 (지정된 경우)
        if log_file:
            # 로그 디렉토리 생성
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """DEBUG 레벨 로그"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """INFO 레벨 로그"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """WARNING 레벨 로그"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """ERROR 레벨 로그"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """CRITICAL 레벨 로그"""
        self.logger.critical(message)
    
    def exception(self, message: str):
        """예외 정보와 함께 로그 출력"""
        self.logger.exception(message)


def get_logger(name: str, log_level: str = "INFO", log_file: Optional[str] = None) -> Logger:
    """
    로거 인스턴스를 반환하는 팩토리 함수
    
    Args:
        name: 로거 이름
        log_level: 로그 레벨
        log_file: 로그 파일 경로
        
    Returns:
        Logger 인스턴스
    """
    return Logger(name, log_level, log_file)


# 기본 로거 설정
def setup_default_logger(name: str = "asset_tracker", log_level: str = "INFO"):
    """
    기본 로거 설정
    
    Args:
        name: 로거 이름
        log_level: 로그 레벨
    """
    # 로그 디렉토리 생성
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 로그 파일명 (날짜 포함)
    today = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{name}_{today}.log")
    
    return get_logger(name, log_level, log_file)


if __name__ == "__main__":
    # 테스트 코드
    logger = setup_default_logger("test_logger", "DEBUG")
    
    logger.info("로거 테스트 시작")
    logger.debug("디버그 메시지")
    logger.warning("경고 메시지")
    logger.error("에러 메시지")
    
    try:
        1 / 0
    except Exception as e:
        logger.exception("예외 발생")
    
    logger.info("로거 테스트 완료") 