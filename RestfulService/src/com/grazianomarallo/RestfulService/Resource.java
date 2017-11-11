package com.grazianomarallo.RestfulService;

<<<<<<< HEAD
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




=======
public abstract class Resource {
    private int capacity;
    private int busyLevel;
    private BaseInfo informations;

    public Resource(int capacity, BaseInfo informations) {
        this.capacity = capacity;
        this.busyLevel = 0;
        this.informations = informations;
    }

    public int getCapacity() {
        return capacity;
    }

    public void setCapacity(int capacity) {
        this.capacity = capacity;
    }

    public int getBusyLevel() {
        return busyLevel;
    }

    public void setBusyLevel(int busyLevel) {
        this.busyLevel = busyLevel;
    }

    public BaseInfo getInformations() {
        return informations;
    }

    public void setInformations(BaseInfo informations) {
        this.informations = informations;
    }
>>>>>>> master
}
