package com.dlut.ResearchService.entity.constants;

public class Regex {
    //大工邮箱
    public static final String DLUT_MAIL = ".*@(mail\\.dlut\\.edu\\.cn|dlut\\.edu\\.cn)$";
    // 纯数字
    public static final String DIGIT_REGEX = "[0-9]+";
    // 含有数字
    public static final String CONTAIN_DIGIT_REGEX = ".*[0-9].*";
    // 含有数字字母
    public static final String CONTAIN_LETTER_REGEX = ".*[0-9a-zA-Z].*";
    // 纯字母
    public static final String LETTER_REGEX = "[a-zA-Z]+";
    // 纯中文
    public static final String CHINESE_REGEX = "[一-龥]";
    // 标准字段检索式
    public static final String FORMAT_QUERY = "[a-z]{2} *=.*";
    // 判断是否正确使用布尔操作符
    public static final String FALSE_BOOLEAN_FORMAT = " *(and|not|or).*(^\\)) *[a-z]{2}=";
    public static final String TS_FORMAT = " *ts *=(.*?)(?=\\)|\\s+(?=AND|OR|NOT)\\b|$)";
    // 判断一个检索式匹配格式
    public static final String JUDGE_ONLY_ONE_CONDITION_WITHOUT_BOOLEAN = "^(\\(| )*[a-z]{2} *=((?! and | not | or ).)*$";
    public static final String MATCH_ONLY_ONE_CONDITION_WITHOUT_BOOLEAN = "[a-z]{2} *=((?! and | not | or ).)*$";
    public static final String JUDGE_ONLY_ONE_CONDITION_WITH_BOOLEAN = "^(\\(| )*[a-z]{2} *=(.*( and | or | not ).*)*$";
    public static final String MATCH_ONLY_ONE_CONDITION_WITH_BOOLEAN = "[a-z]{2} *=(.*( and | or | not ).*)*$";
    public static final String MATCH_MULTI_CONDITION = "[a-z]{2} *=.*(and|or|not) *(\\(| *)[a-z]{2} *=";
    public static final String MATCH_BRACKET = "= *(\\(|\\))";
    public static final String TRUE_BOOLEAN_FORMAT = "(and|or|not) *(?=[a-z]{2} *=)";
    // 匹配and字段
    public static final String MATCH_OPERATOR = "(and|or|not)(?= *(\\([a-z]{2} *=|[a-z]{2} *=))";
}
