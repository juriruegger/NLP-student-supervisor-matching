export type Supervisor = {
  uuid: string;
  email?: string;
  name?: string;
  imageUrl?: string;
  organisationalUnits?: string;
};

export type StaffOrganizationAssociation = {
  organization?: {
    uuid?: string;
  };
  emails?: Array<{
    value: string;
  }>;
};

export type OrganisationalUnit = {
  name: string;
  url: string;
};

export type Organisation = {
  name: {
    en_GB?: string;
    da_DK?: string;
  };
  portalUrl: string;
};

export type OrganisationalUnits = OrganisationalUnit[];

export type TopPaper = {
  title: string;
  url: string;
  similarity: number;
};

export type Keyword = {
  pureId: number;
  locale: string;
  freeKeywords: string[];
};

export type KeyWords = string[];

export type KeywordGroup = {
  typeDiscriminator: string;
  pureId: number;
  logicalName: string;
  name: {
    en_GB: string;
    da_DK: string;
  };
  keywords: Keyword[];
};

export type Suggestion = {
  similarity: number;
  contacted: boolean;
  name: string;
  firstName: string;
  email: string;
  imageUrl: string;
  organisationalUnits: OrganisationalUnits;
  uuid: string;
  topPaper: TopPaper;
  keywords: string[];
};

export type Suggestions = Suggestion[];

export type Topic = {
  topicId: number;
  keywords: string[];
  label: string;
};

export type Topics = Topic[];

export type ProjectType = "specific" | "general";
