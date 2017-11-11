package com.grazianomarallo.RestfulService;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Created by grazianomarallo on 11/11/2017.
 */
public class Resource {

    private static Map<String,Cafeteria> cafeterias  = new ConcurrentHashMap<String,Cafeteria>();
    private static Map<String,Classroom> classrooms = new ConcurrentHashMap<String,Classroom>();
    private static Map<String,Lab> labs = new ConcurrentHashMap<String,Lab>();



    public static Map<String, Cafeteria> getCafeteria() {
        return cafeterias;
    }

    public static Map<String, Lab> getLab() {
        return labs;
    }


    public static Map<String, Classroom> getClassrooms() {
        return classrooms;
    }




}
