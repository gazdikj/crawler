CREATE DATABASE CrawlerDB;
GO

USE CrawlerDB;
GO

-- Tabulka pro podporovaný webový driver
CREATE TABLE WebDriver (
    WebDriverID INT PRIMARY KEY IDENTITY,
    Name NVARCHAR(50) NOT NULL
);

-- Tabulka pro podporované zaøízení
CREATE TABLE Device (
    DeviceID INT PRIMARY KEY IDENTITY,
    Name NVARCHAR(50) NOT NULL
);

-- Tabulka crawleru (každý crawler bude mít vlastní tøídu)
CREATE TABLE Crawler (
    CrawlerID INT PRIMARY KEY IDENTITY,
    Name NVARCHAR(100) NOT NULL,
    ClassName NVARCHAR(200) NOT NULL -- Název tøídy v kódu
);

-- Tabulka pro jednotlivý crawl job
CREATE TABLE CrawlJob (
    JobID INT PRIMARY KEY IDENTITY,
    WebURL NVARCHAR(100) NOT NULL,
	Keyword NVARCHAR(100) NOT NULL,
    StartTime DATETIME DEFAULT GETDATE(),
    EndTime DATETIME NULL,
	CrackCount INT NULL,
    CrawlerID INT NOT NULL,
    WebDriverID INT NOT NULL,
    DeviceID INT NOT NULL,
    FOREIGN KEY (CrawlerID) REFERENCES Crawler(CrawlerID),
    FOREIGN KEY (WebDriverID) REFERENCES WebDriver(WebDriverID),
    FOREIGN KEY (DeviceID) REFERENCES Device(DeviceID)
);

-- Tabulka pro unikátní hash souboru (zabraòuje duplikaci hash hodnot)
CREATE TABLE FileHash (
    HashID INT PRIMARY KEY IDENTITY,
    FileHash NVARCHAR(64) NOT NULL UNIQUE
);

-- Tabulka pro ukládání staženého souboru
CREATE TABLE Crack (
    CrackID INT PRIMARY KEY IDENTITY,    
    Title NVARCHAR(255) NOT NULL,
    Size BIGINT NOT NULL,
    Extension NVARCHAR(10) NOT NULL,  
    CreatedAt DATETIME DEFAULT GETDATE(),
	JobID INT NOT NULL,
	HashID INT NULL,
    FOREIGN KEY (JobID) REFERENCES CrawlJob(JobID),
    FOREIGN KEY (HashID) REFERENCES FileHash(HashID)
);

-- Tabulka pro ukládání chyby pøi crawl procesu
CREATE TABLE Error (
    ErrorID INT PRIMARY KEY IDENTITY, 
    ErrorMessage NVARCHAR(500) NOT NULL,
    OccurredAt DATETIME DEFAULT GETDATE(),
	CrackID INT NOT NULL,
    FOREIGN KEY (CrackID) REFERENCES Crack(CrackID)
);

-- Index pro rychlejší vyhledávání souborù podle hashe
CREATE INDEX IDX_FileHash_FileHash ON FileHash(FileHash);
