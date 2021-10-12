DELETE FROM dbo.Club;

BULK INSERT dbo.Club
   FROM 'C:\Users\Simon Wahlström\Documents\Projects\DataScraping\master_files\club.csv'  
   WITH   
      (  
	     FIRSTROW = 2,
		 CODEPAGE = '65001',
		 DATAFILETYPE = 'widechar',
         FIELDTERMINATOR =',',  
         ROWTERMINATOR ='\n'  
      );
GO