// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'stream_data.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StreamData _$StreamDataFromJson(Map<String, dynamic> json) => StreamData(
      away: json['away'] as bool,
    )
      ..switch1Content = json['switch1Content'] == null
          ? null
          : DisplayContent.fromJson(
              json['switch1Content'] as Map<String, dynamic>?)
      ..switch2Content = json['switch2Content'] == null
          ? null
          : DisplayContent.fromJson(
              json['switch2Content'] as Map<String, dynamic>?)
      ..switch3Content = json['switch3Content'] == null
          ? null
          : DisplayContent.fromJson(
              json['switch3Content'] as Map<String, dynamic>?)
      ..switch1HuntId = json['switch1_hunt_id'] as num?
      ..switch2HuntId = json['switch2_hunt_id'] as num?
      ..switch3HuntId = json['switch3_hunt_id'] as num?;

Map<String, dynamic> _$StreamDataToJson(StreamData instance) =>
    <String, dynamic>{
      'away': instance.away,
      'switch1Content': instance.switch1Content?.toJson(),
      'switch2Content': instance.switch2Content?.toJson(),
      'switch3Content': instance.switch3Content?.toJson(),
      'switch1_hunt_id': instance.switch1HuntId,
      'switch2_hunt_id': instance.switch2HuntId,
      'switch3_hunt_id': instance.switch3HuntId,
    };
